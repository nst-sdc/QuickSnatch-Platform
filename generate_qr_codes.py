import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

# QR code data from our app
QR_CODES = {
    1: "DENTAL_CLINIC_STATUE",
    2: "TEMPLE_GARDEN_PEACE",
    3: "SECURITY_HUT_DENTAL",
    4: "GREEN_PATCH_SHOLAY",
    5: "LIBRARY_FIELD_CORNER",
    6: "MAIN_BUILDING_STATUE",
    7: "BUS_STOP_ENTRANCE",
    8: "PRESS_GREEN_PATCH",
    9: "ATM_LIBRARY_FRONT",
    10: "MAIN_CAFETERIA_2025",
    11: "OLD_CANTEEN_PRINT",
    12: "SWIMMING_POOL_ADYPU",
    13: "RAINBOW_STAIRS_2025",
    14: "LUXURY_CAFE_CORNER",
    15: "SPORTS_PARKING_VIEW",
    16: "RESTRICTED_GATE_25"
}

LOCATION_HINTS = {
    1: """Where laughter's crafted and teeth align,  
A silent guardian bides her time.  
Cloaked in white, serene, and still,  
Behind the halls where smiles are filled.""",
    # ... Add other hints as needed
}

def generate_qr_with_label(data, location_number, output_dir="qr_codes"):
    """Generate a QR code with a label and location number."""
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to RGB mode for adding colored elements
    qr_image = qr_image.convert('RGB')
    
    # Create a new image with space for label
    label_height = 100
    new_image = Image.new('RGB', (qr_image.size[0], qr_image.size[1] + label_height), 'white')
    
    # Paste QR code
    new_image.paste(qr_image, (0, 0))
    
    # Add text
    draw = ImageDraw.Draw(new_image)
    
    # Try to use a nice font, fallback to default if not available
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Add location number and code
    label_text = f"Location {location_number}\n{data}"
    
    # Calculate text position (centered)
    text_bbox = draw.textbbox((0, 0), label_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (new_image.size[0] - text_width) // 2
    text_y = qr_image.size[1] + 20
    
    # Draw text
    draw.text((text_x, text_y), label_text, font=font, fill="black", align="center")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the image
    output_path = os.path.join(output_dir, f"location_{location_number}_qr.png")
    new_image.save(output_path)
    return output_path

def generate_all_qr_codes():
    """Generate QR codes for all locations."""
    print("Generating QR codes...")
    generated_files = []
    
    for location_number, qr_data in QR_CODES.items():
        output_path = generate_qr_with_label(qr_data, location_number)
        generated_files.append(output_path)
        print(f"Generated QR code for Location {location_number}: {output_path}")
    
    print(f"\nGenerated {len(generated_files)} QR codes successfully!")
    print("You can find the QR codes in the 'qr_codes' directory.")

def test_qr_code_reading():
    """Test if generated QR codes can be read correctly."""
    try:
        from pyzbar.pyzbar import decode
        print("\nTesting QR code readability...")
        
        for location_number, qr_data in QR_CODES.items():
            qr_path = f"qr_codes/location_{location_number}_qr.png"
            if os.path.exists(qr_path):
                img = Image.open(qr_path)
                decoded = decode(img)
                if decoded:
                    result = decoded[0].data.decode('utf-8')
                    if result == qr_data:
                        print(f"✓ Location {location_number}: QR code reads correctly")
                    else:
                        print(f"✗ Location {location_number}: QR code mismatch!")
                        print(f"  Expected: {qr_data}")
                        print(f"  Got: {result}")
                else:
                    print(f"✗ Location {location_number}: Could not decode QR code!")
            else:
                print(f"✗ Location {location_number}: QR code file not found!")
    except ImportError:
        print("\nNote: Install 'pyzbar' package to test QR code reading:")
        print("pip install pyzbar")

if __name__ == "__main__":
    # Generate all QR codes
    generate_all_qr_codes()
    
    # Test QR code reading (if pyzbar is installed)
    test_qr_code_reading()
    
    print("\nInstructions for use:")
    print("1. Print these QR codes in high quality")
    print("2. Laminate them for weather protection")
    print("3. Place each QR code at its corresponding location")
    print("4. Test scanning with multiple devices to ensure readability")
    print("\nQR Code Locations and Their Codes:")
    for location, code in QR_CODES.items():
        print(f"Location {location:2d}: {code}")
