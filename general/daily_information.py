from PIL import Image, ImageDraw, ImageFont
import os
from datetime import timedelta
import investpy
from developer_functions.general_dev.massage_and_img_send import send_message_to_all_users, send_image_to_all_users
import yfinance as yf
from datetime import datetime

def get_market_indicators_price_changes():
    """Fetches price and percentage changes for major market indicators including stocks, forex, metals, and commodities."""
    try:
        # Список основних індикаторів ринку
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

        # Формування заголовку таблиці
        lines = [
            "Market Indicators Price Changes",
            "Indicator      | Price     | Change (%)",
            "-" * 45
        ]

        for name, ticker in market_indicators.items():
            data = yf.Ticker(ticker)
            history = data.history(period="5d")  # Отримуємо історію цін за останні 5 днів

            if len(history) >= 2:
                # Поточна ціна (останнє значення закриття)
                current_price = history['Close'].iloc[-1]
                # Обчислення зміни у відсотках між останнім і передостаннім закриттям
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
        return f"Error fetching market indicators: {e}"

# Використання функції для отримання даних
print(get_market_indicators_price_changes())


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
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            img_width, img_height = img.size

            # Load font and dynamically adjust size if necessary
            try:
                font = ImageFont.truetype("arial.ttf", initial_font_size)
            except IOError:
                print("Font 'arial.ttf' not found, using default font.")
                font = ImageFont.load_default()

            # Split text into lines and columns for processing
            lines = table_text.split('\n')
            columns = [line.split('|') for line in lines if '|' in line]

            # Calculate max column widths
            num_columns = len(columns[0])
            col_widths = [0] * num_columns

            for col_idx in range(num_columns):
                col_widths[col_idx] = max(
                    draw.textbbox((0, 0), col[col_idx].strip(), font=font)[2] for col in columns
                )

            # Adjust column widths and font size to fit the image width
            while sum(col_widths) + padding * (num_columns - 1) > img_width:
                initial_font_size -= 1
                font = ImageFont.truetype("arial.ttf", initial_font_size) if initial_font_size > 10 else ImageFont.load_default()
                col_widths = [max(
                    draw.textbbox((0, 0), col[col_idx].strip(), font=font)[2] for col in columns
                ) for col_idx in range(num_columns)]

            # Calculate starting x position and center the table on the image
            total_table_width = sum(col_widths) + padding * (num_columns - 1)
            start_x = (img_width - total_table_width) // 2
            y_position = (img_height - len(lines) * (initial_font_size + padding)) // 2

            # Draw each line of the table
            for line in columns:
                x_position = start_x
                for col, max_width in zip(line, col_widths):
                    col = col.strip()
                    # Truncate text if it exceeds the column width
                    while draw.textbbox((0, 0), col, font=font)[2] > max_width:
                        col = col[:-1] + "…"
                    draw.text((x_position, y_position), col, font=font, fill="white")
                    x_position += max_width + padding
                y_position += initial_font_size + padding

            output_image_path = os.path.join(output_folder, f"market_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            img.save(output_image_path)
            return output_image_path

    except Exception as e:
        print(f"Error creating image: {e}")
        return None


def send_daily_events():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMG_FOLDER = os.path.join(BASE_DIR, 'img', 'daily_news')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'img', 'daily_news_output')
    test_image_path = os.path.join(IMG_FOLDER, 'img1.jpg')
    pre_market_text = ("Preparation is the key to success! 🚀 Here are the important events that could impact the market"
                       " today. Stay sharp, stay confident, and trade wisely. Good luck! 💪")

    send_message_to_all_users(pre_market_text)
    events_text = get_economic_events()
    result_path = overlay_text_on_image(events_text, test_image_path, OUTPUT_FOLDER)
    send_image_to_all_users(result_path)


def send_day_end_info():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMG_FOLDER = os.path.join(BASE_DIR, 'img', 'daily_news')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'img', 'daily_news_output')
    test_image_path = os.path.join(IMG_FOLDER, 'end.jpg')
    post_market_text = ("🌅 The trading day comes to an end, but every moment is a learning experience. "
                        "Check out today's market changes, reflect, and get ready for new opportunities "
                        "tomorrow. Stay strong! 🔥")

    send_message_to_all_users(post_market_text)
    events_text = get_market_indicators_price_changes()
    result_path = overlay_text_on_image(events_text, test_image_path, OUTPUT_FOLDER)
    send_image_to_all_users(result_path)

