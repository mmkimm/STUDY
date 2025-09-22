from faker import Faker
import pandas as pd
import random
from tabulate import tabulate   # 👈 추가

def generate_people(num=10):
    fake = Faker('ko_KR')
    data = []
    for _ in range(num):
        person = {
            "이름": fake.name(),
            "주소": fake.address().replace("\n", " "),
            "전화번호": fake.phone_number(),
            "이메일": fake.email(),
            "직업": fake.job(),
            "나이": random.randint(20, 60)
        }
        data.append(person)
    return pd.DataFrame(data)

def main():
    df = generate_people(10)
    df_sorted = df.sort_values(by=["이름", "나이"]).reset_index(drop=True)

    print("=== 정렬된 10명 기본정보 ===")
    # tabulate로 예쁘게 출력
    print(tabulate(df_sorted, headers="keys", tablefmt="pretty", showindex=False))

if __name__ == "__main__":
    main()
