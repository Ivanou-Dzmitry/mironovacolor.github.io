import os
from bs4 import BeautifulSoup
import sys

def process_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    # Your existing processing code here
    # Remove width, height, border attrs from img tags
    for img in soup.find_all("img"):
        for attr in ["width", "height", "border"]:
            if attr in img.attrs:
                del img[attr]

    # Remove empty <tr> and <td>
    for tag in soup.find_all(["tr", "td"]):
        if not tag.find_all(True) and not tag.get_text(strip=True):
            tag.decompose()

    # Unwrap tables, trs, tds
    for tag_name in ["table", "tr", "td"]:
        for tag in soup.find_all(tag_name):
            tag.unwrap()

    # Wrap img + next <a> text sibling into div.caption
    imgs = soup.find_all("img")
    for img in imgs:
        next_sib = img.find_next_sibling()
        if next_sib and next_sib.name == "a" and next_sib.get_text(strip=True):
            div = soup.new_tag("div", attrs={"class": "caption"})
            img.insert_after(div)
            div.append(img.extract())
            div.append(next_sib.extract())

    # Replace <a> text-only with div.caption
    for a in soup.find_all("a"):
        if a.find("img"):
            continue
        caption = soup.new_tag("div", **{"class": "caption"})
        caption.string = a.get_text(strip=True)
        a.replace_with(caption)

    # Replace <a><img></a> with just <img>
    for a in soup.find_all("a"):
        img = a.find("img")
        if img:
            a.replace_with(img)
        else:
            caption = soup.new_tag("div", **{"class": "caption"})
            caption.string = a.get_text(strip=True)
            a.replace_with(caption)

    # Remove consecutive <br><br>
    for br in soup.find_all("br"):
        next_sibling = br.find_next_sibling()
        if next_sibling and next_sibling.name == "br":
            next_sibling.extract()
            br.extract()

    # Fix src path for images
    for img in soup.find_all("img"):
        if img.has_attr("src") and img["src"].startswith("thumbnails/"):
            img["src"] = img["src"].replace("thumbnails/", "images/")

    return str(soup)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for filename in os.listdir(current_dir):
        if filename.lower().endswith(".html"):
            input_path = os.path.join(current_dir, filename)
            output_path = os.path.join(current_dir, "cleaned_" + filename)

            with open(input_path, encoding="utf-8") as f:
                html = f.read()

            cleaned_html = process_html(html)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_html)

            print(f"Processed {filename} -> {output_path}")
