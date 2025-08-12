import heapq
import os
import pickle

class HuffmanCoding:
    def __init__(self, file_path):
        self.file_path = file_path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}

    class HeapNode:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq

    def _build_frequency_dict(self, text):
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        return frequency

    def _build_heap(self, frequency):
        for char, freq in frequency.items():
            heapq.heappush(self.heap, self.HeapNode(char, freq))

    def _merge_nodes(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            merged = self.HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(self.heap, merged)

    def _build_codes_helper(self, root, current_code):
        if root is None:
            return
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        self._build_codes_helper(root.left, current_code + "0")
        self._build_codes_helper(root.right, current_code + "1")

    def _build_codes(self):
        root = heapq.heappop(self.heap)
        self._build_codes_helper(root, "")

    def _get_encoded_text(self, text):
        return "".join(self.codes[char] for char in text)

    def _pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        encoded_text += "0" * extra_padding
        padded_info = "{0:08b}".format(extra_padding)
        return padded_info + encoded_text

    def _get_byte_array(self, padded_encoded_text):
        return bytearray(int(padded_encoded_text[i:i+8], 2) for i in range(0, len(padded_encoded_text), 8))

    def compress(self):
        
        output_path = self.file_path + ".bin"

        try:
            with open(self.file_path, 'r', encoding="utf-8") as file:
                text = file.read()
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return None

        frequency = self._build_frequency_dict(text)
        self._build_heap(frequency)
        self._merge_nodes()
        self._build_codes()

        encoded_text = self._get_encoded_text(text)
        padded_encoded_text = self._pad_encoded_text(encoded_text)
        byte_array = self._get_byte_array(padded_encoded_text)

        try:
            with open(output_path, 'wb') as output:
                pickle.dump((self.reverse_mapping, byte_array), output)

        except Exception as e:
            print(f"Error writing compressed file: {e}")
            return None

        return output_path

    def _remove_padding(self, padded_bit_string):
        padded_info = padded_bit_string[:8]
        extra_padding = int(padded_info, 2)
        return padded_bit_string[8:-extra_padding]

    def _decode_text(self, bit_string):
        decoded_text = ""
        current_code = ""
        for bit in bit_string:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_text += self.reverse_mapping[current_code]
                current_code = ""
        return decoded_text

    def decompress(self):
        
        output_path = self.file_path.replace(".bin", "_decompressed.txt")

        try:
            with open(self.file_path, 'rb') as file:
                self.reverse_mapping, byte_array = pickle.load(file)

            bit_string = "".join(f"{byte:08b}" for byte in byte_array)
            unpadded_bit_string = self._remove_padding(bit_string)
            decoded_text = self._decode_text(unpadded_bit_string)

            with open(output_path, 'w', encoding="utf-8") as output:
                output.write(decoded_text)

            return output_path

        except pickle.UnpicklingError:
            print(f"Decompression error: The file '{self.file_path}' is corrupted.")
            return None

        except Exception as e:
            print(f"Decompression error: {e}")
            return None
