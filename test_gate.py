from app.gate_utils import gate_decision

print("Car test:")
print(gate_decision("test_images/car.jpeg"))

print("\nTomato test:")
print(gate_decision("test_images/tomatoleaf_image.PNG"))