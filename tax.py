# 상품 목록
products = [
    {"name": "노트북", "price": 1000000},
    {"name": "스마트폰", "price": 800000},
    {"name": "헤드폰", "price": 200000},
]

def format_currency(amount):
    return f"{amount:,}원"  # 1,000,000원 형태

def show_products():
    print("=== 상품 목록 ===")
    for i, p in enumerate(products, 1):
        print(f"{i}. {p['name']} - 단가: {format_currency(p['price'])}")
    print("================\n")

def estimate(product_name, quantity=1):
    product = next((p for p in products if p["name"] == product_name), None)
    if not product:
        print(f"'{product_name}' 상품을 찾을 수 없습니다.")
        return
    subtotal = product["price"] * quantity
    tax = int(subtotal * 0.1)
    total = subtotal + tax
    print("\n=== 견적 결과 ===")
    print(f"상품: {product_name}")
    print(f"단가: {format_currency(product['price'])}")
    print(f"수량: {quantity}")
    print(f"소계: {format_currency(subtotal)}")
    print(f"세금(10%): {format_currency(tax)}")
    print(f"총합: {format_currency(total)}")
    print("================\n")

if __name__ == "__main__":
    show_products()
    product_name = input("상품명을 입력하세요: ")
    quantity = int(input("수량을 입력하세요: "))
    estimate(product_name, quantity)
