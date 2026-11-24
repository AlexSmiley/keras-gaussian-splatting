import pytest
from gsplat_keras.youtube import canonical_url

@pytest.mark.parametrize("url", ["https://youtu.be/abcdefghijk", "https://www.youtube.com/watch?v=abcdefghijk&t=10", "https://youtube.com/shorts/abcdefghijk"])
def test_valid(url):
    assert canonical_url(url) == "https://www.youtube.com/watch?v=abcdefghijk"

@pytest.mark.parametrize("url", ["https://youtube.com.evil.test/watch?v=abcdefghijk", "http://youtu.be/abcdefghijk", "https://youtu.be/short", "https://youtube.com@evil.test/watch?v=abcdefghijk"])
def test_invalid(url):
    with pytest.raises(ValueError):
        canonical_url(url)
