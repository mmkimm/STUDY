# 고객 목록
customers = [
    {"name": "김민수", "age": 29, "address": "경기도 성남시 판교", "phone": "010-1234-5678"},
    {"name": "이서연", "age": 34, "address": "서울시 강남구", "phone": "010-2345-6789"},
    {"name": "박준영", "age": 41, "address": "인천시 연수구", "phone": "010-3456-7890"}
]

# 상품 목록
products = [
    {"name": "수제 버거", "price": 8500, "description": "수제로 만든 패티와 신선한 채소"},
    {"name": "감자튀김", "price": 3000, "description": "바삭한 프렌치프라이"},
    {"name": "수제 맥주(500ml)", "price": 7000, "description": "지역 수수제 맥주"}
]

def show_all():
    print("\n=== 전체 정보 ===")
    print("\n-- 고객 목록 --")
    for c in customers:
        print(f"{c['name']} | 나이: {c['age']} | 주소: {c['address']} | 전화: {c['phone']}")
    
    print("\n-- 상품 목록 --")
    for p in products:
        print(f"{p['name']} | 단가: {p['price']}원 | 설명: {p['description']}")
    print("================\n")

def search_customers():
    query = input("검색할 고객명을 입력하세요 (전체조회는 Enter): ")
    result = [c for c in customers if query.lower() in c["name"].lower()]
    if not result:
        print("검색 결과가 없습니다.")
    else:
        print("\n-- 검색 결과 --")
        for c in result:
            print(f"{c['name']} | 나이: {c['age']} | 주소: {c['address']} | 전화: {c['phone']}")
    print("================\n")

def search_products():
    query = input("검색할 상품명을 입력하세요 (전체조회는 Enter): ")
    result = [p for p in products if query.lower() in p["name"].lower()]
    if not result:
        print("검색 결과가 없습니다.")
    else:
        print("\n-- 검색 결과 --")
        for p in result:
            print(f"{p['name']} | 단가: {p['price']}원 | 설명: {p['description']}")
    print("================\n")

# 메인 메뉴
def menu():
    while True:
        print("=== 메뉴 ===")
        print("1. 전체 정보 조회")
        print("2. 고객 검색")
        print("3. 상품 검색")
        print("0. 종료")
        choice = input("선택하세요: ")
        
        if choice == "1":
            show_all()
        elif choice == "2":
            search_customers()
        elif choice == "3":
            search_products()
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 입력하세요.\n")

if __name__ == "__main__":
    menu()
