import scrapy
from scrapy.http import Request

class BookSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["fahasa.com"]
    
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "DOWNLOAD_DELAY": 0.5  # Add delay of 1.5 seconds between requests
    }

    def start_requests(self):
        # Start from page 1 and go up until no books are left
        for page in range(1, 1009):  # Arbitrary large number; stop when no more pages
            url = f"https://www.fahasa.com/sach-trong-nuoc.html?order=num_orders&limit=48&p={page}"
            yield Request(url, callback=self.parse)

    def parse(self, response):
        # Extract book names and links
        books = response.css('h2.product-name-no-ellipsis.p-name-list a')
        if not books:
            return  # Stop the spider if no books found (last page reached)
        
        for book in books:
            book_name = book.css('::attr(title)').get()
            book_link = book.css('::attr(href)').get()
            full_link = response.urljoin(book_link)
            yield Request(full_link, callback=self.parse_book_detail, meta={'book_name': book_name})

    def parse_book_detail(self, response):
        book_name = response.meta['book_name']
        price = response.css('p.special-price span.price::text').get(default="Not Found").strip()
        old_price = response.css('p.old-price span.price::text').get(default="Not Found").strip()
        discount = response.css('span.discount-percent::text').get(default="Not Found").strip()
        rating = response.css('div.icon-star-text::text').get(default="Not Found").strip()
        number_of_votes = response.css('p.rating-links a::text').re_first(r'\d+').strip() if response.css('p.rating-links a::text') else "Not Found"
        quantity_sold = response.css('div.product-view-qty-num::text').get(default="Not Found").strip()
        product_id = response.css('td.data_sku::text').get(default="Not Found").strip()
        
        # Corrected extraction for Tác Giả
        tac_gia = response.css('td.data_author div.attribute_link_container::text').get(default="Not Found").strip()
        
        nha_san_xuat = response.css('td.data_supplier div.attribute_link_container a::text').get(default="Not Found").strip()
        nha_xuat_ban = response.css('td.data_publisher::text').get(default="Not Found").strip()
        nam_xuat_ban = response.css('td.data_publish_year::text').get(default="Not Found").strip()
        ngon_ngu = response.css('td.data_languages div.attribute_link_container::text').get(default="Not Found").strip()
        trong_luong = response.css('td.data_weight::text').get(default="Not Found").strip()
        kich_thuoc = response.css('td.data_size::text').get(default="Not Found").strip()
        so_trang = response.css('td.data_qty_of_page::text').get(default="Not Found").strip()
        loai_bia = response.css('td.data_book_layout div.attribute_link_container::text').get(default="Not Found").strip()
        age_restriction = response.css('td.data_age div.attribute_link_container::text').get(default="Not Found").strip()

        # Extract categories from breadcrumb <ol> list
        category1 = response.css('ol.breadcrumb li:nth-child(1) a::text').get(default="Not Found").strip()
        category2 = response.css('ol.breadcrumb li:nth-child(2) a::text').get(default="Not Found").strip()
        category3 = response.css('ol.breadcrumb li:nth-child(3) a::text').get(default="Not Found").strip()

        yield {
            "Book Name": book_name,
            "Category 1": category1,  # First category in breadcrumb
            "Category 2": category2,  # Second category in breadcrumb
            "Category 3": category3,   # Third category in breadcrumb
            "Price": price,
            "Old Price": old_price,
            "Discount": discount,
            "Rating": rating,
            "Number of Votes": number_of_votes,
            "Quantity Sold": quantity_sold,
            "Product ID": product_id,
            "Tác Giả": tac_gia,  # Updated extraction for Tác Giả
            "Nhà Sản Xuất": nha_san_xuat,
            "Nhà Xuất Bản": nha_xuat_ban,
            "Năm Xuất Bản": nam_xuat_ban,
            "Ngôn Ngữ": ngon_ngu,
            "Trọng Lượng": trong_luong,
            "Kích Thước": kich_thuoc,
            "Số Trang": so_trang,
            "Loại Bìa": loai_bia,
            "Độ tuổi": age_restriction
        }
