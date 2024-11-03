from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
import investpy

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

def overlay_text_on_image(text, image_path, output_folder, font_size=25):
    """Overlays formatted text on an image and aligns it as an Excel-like table."""
    os.makedirs(output_folder, exist_ok=True)
    clear_folder(output_folder)

    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            img_width, img_height = img.size

            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                print("Font 'arial.ttf' not found, using default font.")
                font = ImageFont.load_default()

            # Split lines and create a 2D array for better formatting
            lines = text.split('\n')
            columns = [line.split('|') for line in lines]

            # Calculate max width for each column
            col_widths = []
            for col_idx in range(len(columns[0])):
                max_width = max(draw.textbbox((0, 0), col[col_idx].strip(), font=font)[2] for col in columns)
                col_widths.append(max_width)

            # Calculate total table width for centering
            total_table_width = sum(col_widths) + (10 * (len(col_widths) - 1))
            start_x = (img_width - total_table_width) // 2
            y_position = (img_height - len(lines) * (font_size + 10)) // 2

            for line in columns:
                x_position = start_x
                for col, max_width in zip(line, col_widths):
                    col = col.strip()
                    draw.text((x_position, y_position), col, font=font, fill="white")
                    x_position += max_width + 10
                y_position += font_size + 10

            output_image_path = os.path.join(output_folder, f"market_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            img.save(output_image_path)
            return output_image_path

    except Exception as e:
        print(f"Error creating image: {e}")
        return None




# Example usage
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMG_FOLDER = os.path.join(BASE_DIR, 'img', 'daily_news')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'img', 'daily_news_output')
    test_image_path = os.path.join(IMG_FOLDER, 'img1.jpg')

    if os.path.exists(test_image_path):
        events_text = get_economic_events()
        result_path = overlay_text_on_image(events_text, test_image_path, OUTPUT_FOLDER)
        if result_path:
            print(f"Image created successfully: {result_path}")
        else:
            print("Failed to create image.")
    else:
        print(f"Test image not found at {test_image_path}.")
