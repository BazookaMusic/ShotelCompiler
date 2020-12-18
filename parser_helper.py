def parse_multiple(element_getter, collection):
    while True:
        element = element_getter()

        if element is None:
            return
        
        collection.append(element_getter())
    
