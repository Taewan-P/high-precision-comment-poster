from cheer import get_cheer_id
from post import get_grp_id

print("--- Test Start ---")
cafe_link = "https://cafe.daum.net/LeeChaeYeon"

cafe_id = get_grp_id(cafe_link)
cheer_id = get_cheer_id(cafe_link)

assert cafe_id == "1ZNFK", f"Wrong Cafe ID! - Expected 1ZNFK, but returned {cafe_id}"
assert cheer_id == 1971, f"Wrong Cheer ID! - Expected 1971, but returned {cheer_id}"

print("Test 1 cleared")

cafe_link = "https://cafe.daum.net/IVEstarship"

cafe_id = get_grp_id(cafe_link)
cheer_id = get_cheer_id(cafe_link)

assert cafe_id == "1ZCQy", f"Wrong Cafe ID! - Expedted 1ZCQy, but returned {cafe_id}"
assert cheer_id == 1806, f"Wrong Cheer ID! - Expected 1806, but returned {cheer_id}"

print("Test 2 cleared")

print("--- Test Passed ---")
