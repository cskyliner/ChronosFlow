from Event import DDLEvent,search_all

test_event1 = DDLEvent("ai引论","2025-4-28","",False,120)

def test_add_event():
    test_event1.add_event()
# test_add_event()
events = search_all("ai")
for event in events:
    print(event.title)
    event.delete_event()
    print(f"{event.id} event deleted")