from heapq import *
from .bit_util import *


# Compresses a list of bytes
def compress(uncompressed):
    if len(uncompressed) == 0:
        # Edge case, could be fixed other ways but cba
        return _compress_empty()
    freqs = _calculate_frequencies(uncompressed)
    hufftree = _assemble_huffman_tree(freqs)
    substitutions = _create_substitution_map(hufftree)
    writer = BitWriter()
    _encode_huffman_tree(writer, hufftree)
    for byte in uncompressed:
        bitcode = substitutions[byte]
        for bit in bitcode:
            writer.push(bit)
    writer = pad(writer)
    compressed, _ = writer.get()
    return compressed


# Decompresses a compressed list of bytes
def decompress(compressed):
    reader = BitReader(compressed)
    unpad(reader)
    hufftree = _decode_huffman_tree(reader)
    current = hufftree
    decompressed = []
    while reader.length() > 0:
        if reader.pop():
            current = current.right
        else:
            current = current.left
        if current.is_leaf():
            decompressed.append(current.byte)
            current = hufftree
    return decompressed


# Returns a padded version of the given BitWriter
def pad(writer):
    written, remainder = writer.get()
    padding_required = 8 - len(remainder)
    reader = BitReader(written, remainder)
    padded = BitWriter()
    for i in range(0, padding_required - 1):
        padded.push(False)
    padded.push(True)
    while reader.length() > 0:
        padded.push(reader.pop())
    return padded


# Strips any padding from the given reader
def unpad(reader):
    while not reader.pop():
        pass


# Calculates the frequencies of various bytes in the given data, returns a dictionary
def _calculate_frequencies(data):
    freqs = {}
    for byte in data:
        if byte not in freqs:
            freqs[byte] = 0
        freqs[byte] += 1
    return freqs


# Assembles a huffman tree from a frequency dictionary
def _assemble_huffman_tree(freqs):
    heap = []
    for byte, freq in freqs.items():
        heappush(heap, HuffmanTree(byte, freq))
    # Pad things out. Can't construct a tree without at least 2 nodes
    for _ in range(0, 2 - len(freqs)):
        heappush(heap, HuffmanTree())
    while len(heap) > 1:
        first = heappop(heap)
        second = heappop(heap)
        total_freq = first.freq + second.freq
        new_parent = HuffmanTree(freq=total_freq)
        new_parent.left = first
        new_parent.right = second
        heappush(heap, new_parent)
    hufftree = heappop(heap)
    return hufftree


# Creates a substitution map (dict) from a huffman tree
def _create_substitution_map(hufftree):
    def traverse(node, subs, bitcode):
        if node is None:
            return
        bitcode.append(False)
        traverse(node.left, subs, bitcode)
        bitcode.pop()
        if node.is_leaf():
            subs[node.byte] = bitcode.copy()
        bitcode.append(True)
        traverse(node.right, subs, bitcode)
        bitcode.pop()
    subs = {}
    traverse(hufftree, subs, [])
    return subs


# Encodes a huffman tree at the start of a BitWriter
def _encode_huffman_tree(writer, hufftree):
    def traverse(node, writer):
        if node is None:
            return
        writer.push(node.is_leaf())
        if node.is_leaf():
            writer.push_byte(node.byte)
        traverse(node.left, writer)
        traverse(node.right, writer)
    traverse(hufftree, writer)


# Decodes a huffman tree from an unpadded BitReader, leaving anything not part of the header
def _decode_huffman_tree(reader):
    parent_stack = []
    if reader.pop():
        return None  # Invalid tree header
    parent_stack.append(HuffmanTree())
    root = parent_stack[-1]
    current = root
    while len(parent_stack) > 0:
        if reader.pop():
            # Leaf, get byte
            if reader.length() < 8:
                return None  # Invalid header
            byte = reader.pop_byte()
            current.add_child(HuffmanTree(byte))
            if current.is_full():
                parent_stack.pop()
                if len(parent_stack) == 0:
                    return root
                current = parent_stack[-1]
        else:
            # Parent
            parent = HuffmanTree()
            current.add_child(parent)
            if current.is_full():
                parent_stack.pop()
            current = parent
            parent_stack.append(parent)
    return root


class HuffmanTree:
    def __init__(self, byte=0, freq=0):
        self.left = None
        self.right = None
        self.byte = byte
        self.freq = freq

    def is_leaf(self):
        return self.left is None and self.right is None

    def is_full(self):
        return self.left is not None and self.right is not None

    def add_child(self, child):
        if self.left is None:
            self.left = child
        elif self.right is None:
            self.right = child

    def __lt__(self, other):
        return self.freq < other.freq


def _compress_empty():
    writer = BitWriter()
    writer.push(False)
    writer.push(True)
    writer.push_byte(0)
    writer.push(True)
    writer.push_byte(0)
    writer = pad(writer)
    compressed, _ = writer.get()
    return compressed

