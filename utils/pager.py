def paginate(items, page=0, page_size=10):
    start = page * page_size
    end = start + page_size
    return items[start:end]
