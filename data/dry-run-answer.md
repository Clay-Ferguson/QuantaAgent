// file_begin /temperature_convert.py
class TemperatureConverter:
    @staticmethod
    def run():
        celsius = float(input("Enter temperature in Celsius: "))
        fahrenheit = (celsius * 9/5) + 32
        print(f"{celsius} degree Celsius is equal to {fahrenheit} degree Fahrenheit.")

if __name__ == "__main__":
    TemperatureConverter.run()
// file_end /temperature_convert.py
