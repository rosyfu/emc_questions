# !/usr/bin/python

class node(object):
    def __init__(self,val):
        self.data = val
        self.next = None
def reverseK(head,k):
    if head is None or head.next is None or k<2:
        return head
    root = node(0)
    start = root
    end = head
    cur = head
    length = 0
    #Reverse every k nodes by insertion
    while cur:
        if length is 0:
            end = cur
        length = length + 1
        curnext = cur.next
        cur.next = start.next
        start.next = cur
        cur = curnext
        #If k nodes done, reset the length and start node
        if length is k:
            start = end
            length = 0
    # Reverse remainder nodes again
    if length is not 0:
        cur = start.next
        start.next = None
        while cur is not None:
            curnext = cur.next
            cur.next = start.next
            start.next = cur
            cur = curnext
    return root.next

if __name__=="__main__":
    num_input = raw_input('Input List Numbers:')
    nums = num_input.split(' ')
    k = input('Input K:')
    head = None
    for num in nums:
        if num is not '':
            if head == None:
                head = node(int(num))
                tail = head
            else:
                tail.next = node(int(num))
                tail = tail.next
    p = reverseK(head,k)
    while p:
        print p.data,
        p = p.next
