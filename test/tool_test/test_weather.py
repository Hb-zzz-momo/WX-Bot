from tools.weather import get_weather


def main():

    city = input("请输入城市：")

    result = get_weather.invoke(
        {
            "city": city
        }
    )

    print("\n天气查询结果：")
    print(result)


if __name__ == "__main__":
    main()