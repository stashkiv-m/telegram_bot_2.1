from PIL import Image, ImageDraw, ImageFont
import os
from datetime import timedelta, datetime
import investpy
import yfinance as yf
from developer_functions.general_dev.massage_and_img_send import send_message_to_all_users, send_image_to_all_users

def get_market_indicators_price_changes():
    """Fetches price and percentage changes for major market indicators including stocks, forex, metals, and commodities."""
    try:
        market_indicators = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'FTSE 100': '^FTSE',
            'DAX': '^GDAXI',
            'USD/EUR': 'EURUSD=X',
            'USD/JPY': 'JPY=X',
            'Bitcoin': 'BTC-USD',
            'Ethereum': 'ETH-USD',
            'Gold': 'GC=F',
            'Silver': 'SI=F',
            'Crude Oil': 'CL=F',
            'Natural Gas': 'NG=F',
            'Copper': 'HG=F'
        }

        lines = [
            "Market Indicators Price Changes",
            "Indicator      | Price     | Change (%)",
            "-" * 45
        ]

        for name, ticker in market_indicators.items():
            data = yf.Ticker(ticker)
            history = data.history(period="5d")

            if len(history) >= 2:
                current_price = history['Close'].iloc[-1]
                change = ((history['Close'].iloc[-1] - history['Close'].iloc[-2]) / history['Close'].iloc[-2]) * 100
                price_text = f"{current_price:.2f}"
                change_text = f"{change:.2f}%"
            else:
                price_text = "N/A"
                change_text = "N/A"

            lines.append(f"{name:<14} | {price_text:<9} | {change_text:<10}")

        lines.append("\n* Data represents the percentage change from the previous day's close.")
        return "\n".join(lines)

    except Exception as e:
        print(f"Error fetching market indicators: {e}")
        return f"Error fetching market indicators: {e}"

def get_economic_events(country='United States', days_ahead=5):
    """Fetches high-importance economic events for a specified country and period."""
    try:
        today = datetime.today()
        from_date = today.strftime('%d/%m/%Y')
        to_date = (today + timedelta(days=days_ahead)).strftime('%d/%m/%Y')
        calendar = investpy.news.economic_calendar(
            countries=[country],
            from_date=from_date,
            to_date=to_date
        )

        if calendar.empty:
            print("No economic events found for the specified period.")
            return "No important events for the specified period."

        important_events = calendar[calendar['importance'] == 'high'][['date', 'time', 'event', 'forecast', 'previous']]
        important_events['date'] = important_events['date'].apply(lambda d: datetime.strptime(d, '%d/%m/%Y').strftime('%d/%m'))

        lines = [
            f"Economic Events ({from_date} - {to_date})",
            "Date      | Time     | Event                           | Forecast   | Previous",
            "-" * 80
        ]

        for _, row in important_events.iterrows():
            event = (row['event'][:30] + '...') if len(row['event']) > 30 else row['event']
            forecast = row['forecast'] or "N/A"
            previous = row['previous'] or "N/A"
            lines.append(f"{row['date']:<9} | {row['time']:<8} | {event:<30} | {forecast:<10} | {previous:<10}")

        lines.append("\n* All times are in Eastern Standard Time (EST)")
        return "\n".join(lines)

    except Exception as e:
        print(f"Error fetching events: {e}")
        return f"Error fetching events: {e}"

def clear_folder(folder_path):
    """Removes all files from a specified folder."""
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def overlay_text_on_image(table_text, image_path, output_folder, initial_font_size=25, padding=10):
    """Overlays formatted table text on an image, aligning columns dynamically and adjusting for image size."""
    os.makedirs(output_folder, exist_ok=True)
    clear_folder(output_folder)

    try:
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'arial.ttf')
        print(f"Path to font: {font_path}")

        if not os.path.exists(font_path):
            print("Font file does not exist at the specified path!")

        try:
            font = ImageFont.truetype(font_path, initial_font_size)
            print("Font loaded successfully.")
        except IOError as e:
            print(f"Font not found at {font_path}. Using default font. Error: {e}")
            font = ImageFont.load_default()

        with Image.open(image_path) as img:
            print("Image opened successfully.")
            draw = ImageDraw.Draw(img)
            img_width, img_height = img.size

            lines = table_text.split('\n')
            print("Number of lines:", len(lines))

            columns = [line.split('|') for line in lines if '|' in line]
            if not columns:
                print("No columns detected. Exiting function.")
                return None

            num_columns = len(columns[0])
            col_widths = [0] * num_columns

            for col_idx in range(num_columns):
                col_widths[col_idx] = max(
                    draw.textbbox((0, 0), col[col_idx].strip(), font=font)[2] for col in columns
                )

            while sum(col_widths) + padding * (num_columns - 1) > img_width:
                initial_font_size -= 1
                if initial_font_size <= 10:
                    font = ImageFont.load_default()
                    print("Reached minimum font size. Using default font.")
                    break
                font = ImageFont.truetype(font_path, initial_font_size)
                col_widths = [max(
                    draw.textbbox((0, 0), col[col_idx].strip(), font=font)[2] for col in columns
                ) for col_idx in range(num_columns)]

            total_table_width = sum(col_widths) + padding * (num_columns - 1)
            start_x = (img_width - total_table_width) // 2
            y_position = (img_height - len(lines) * (initial_font_size + padding)) // 2

            for line in columns:
                x_position = start_x
                for col, max_width in zip(line, col_widths):
                    col = col.strip()
                    while draw.textbbox((0, 0), col, font=font)[2] > max_width:
                        col = col[:-1] + "…"
                    draw.text((x_position, y_position), col, font=font, fill="white")
                    x_position += max_width + padding
                y_position += initial_font_size + padding

            output_image_path = os.path.join(output_folder, f"market_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            img.save(output_image_path)
            print(f"Image saved at: {output_image_path}")

            return output_image_path

    except Exception as e:
        print(f"Error creating image: {e}")
        return None

def send_daily_events():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    img_folder = os.path.join(base_dir, 'img', 'daily_news')
    output_folder = os.path.join(base_dir, 'img', 'daily_news_output')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    input_image_path = os.path.join(img_folder, 'img1.jpg')
    pre_market_text = ("Preparation is the key to success! 🚀 Here are the important events that could impact the market "
                       "today. Stay sharp, stay confident, and trade wisely. Good luck! 💪")
    send_message_to_all_users(pre_market_text)
    events_text = get_economic_events()
    print(f"Events text: {events_text}")
    if not events_text or events_text == "No important events for the specified period.":
        print("No events available or the text is empty.")
        return
    result_path = overlay_text_on_image(events_text, input_image_path, output_folder)
    if result_path:
        send_image_to_all_users(result_path)

def send_day_end_info():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    img_folder = os.path.join(base_dir, 'img', 'daily_news')
    output_folder = os.path.join(base_dir, 'img', 'daily_news_output')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    input_image_path = os.path.join(img_folder, 'end.jpg')
    post_market_text = ("🌅 The trading day comes to an end, but every moment is a learning experience. "
                        "Check out today's market changes, reflect, and get ready for new opportunities "
                        "tomorrow. Stay strong! 🔥")
    send_message_to_all_users(post_market_text)
    events_text = get_market_indicators_price_changes()
    print(f"Events text: {events_text}")
    if not events_text or events_text == "Error fetching market indicators":
        print("No indicators available or an error occurred.")
        return
    result_path = overlay_text_on_image(events_text, input_image_path, output_folder)
    if result_path:
        send_image_to_all_users(result_path)
