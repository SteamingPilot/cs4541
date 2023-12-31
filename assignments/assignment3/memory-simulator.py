import sys
import os

# Global Constants
MEM_ENT_TYPE_PLACEHOLDER = 0
MEM_ENT_TYPE_HEADER = 1
MEM_ENT_TYPE_FOOTER = 2
MEM_ENT_TYPE_PAYLOAD = 3
MEM_ENT_TYPE_EMPTY = 4


INITIAL_MEM_COUNT = 1000
INITIAL_HEADER_LOCATION = 1
HEX_PADDING = 10
PLACEHOLDER_VALUE = 1


WORD_SIZE = 4 
DOUBLE_WORD_SIZE = 8
ALIGNMENT_SIZE = DOUBLE_WORD_SIZE

HF_OVERHEAD = 2*WORD_SIZE
ALLOCATION_SET_BIT = 1
MAX_HEAP_SIZE = 100_000
NONE_LOCATION = 0

ARGUMENT_VERBOSE = 0
ARGUMENT_OUTPUT = 1
ARGUMENT_FREE_LIST = 2
ARGUMENT_FIT = 3
ARGUMENT_INPUT = 4

ARG_VAL_IMPLICIT_LIST = 0
ARG_VAL_EXPLICIT_LIST = 1
ARG_VAL_FIRST_FIT, FIT_FIRST = 0, 0
ARG_VAL_BEST_FIT, FIT_BEST = 1, 1


CMD_IND_OPERATION = 0
CMD_A_IND_OPERATION = 0
CMD_A_IND_SIZE = 1
CMD_A_IND_ADDR = 2
CMD_R_IND_OPERATION = 0
CMD_R_IND_SIZE = 1 
CMD_R_IND_OLD_ADDR = 2
CMD_R_IND_NEW_ADDR = 3
CMD_F_IND_OPERATION = 0
CMD_F_IND_ADDR = 1

FIT_FIRST = 0 
FIT_BEST = 1

PREV_PTR_OFFSET = 1
NEXT_PTR_OFFSET = 2



def printError(message: str):
    if message is not None:
        print(message)
    print("usage: python3 ./memory-simulator.py [-v] [-o <output-path>] --free-list=[implicit or explicit] --fit=[first or best] <input file>")


def getHexStringFromDecimal(decimal, padding=HEX_PADDING):
    tmp = f"{decimal:#0{padding}X}"
    tmp = tmp.replace('X', 'x')
    return tmp

def getDecimalFromHexString(hex_string):
    return int(hex_string, 16)


def alignSize(size):
    if size%ALIGNMENT_SIZE == 0:
        return size
    return size + (ALIGNMENT_SIZE - (size%ALIGNMENT_SIZE))



class MemoryEntry:
    def __init__(self, line: int, type: int, value: str) -> None:
        # type is GLOBAL CONSTANT that indicates the type of a memory entry (Placeholder, header, footer, payload, empty). 
        # It uses the following constants
        # MEM_ENT_TYPE_PLACEHO       
        # MEM_ENT_TYPE_HEADER 
        # MEM_ENT_TYPE_FOOTER 
        # MEM_ENT_TYPE_PAYLOAD
        # MEM_ENT_TYPE_EMPTY 

        self.line = line
        self.type = type        
        self.value = value




class Heap:
    def __init__(self) -> None:
        self.memory = list()
        self.mem_count = 0
        self.free_list = HeapFreeList(self)
        self.address_mapper = dict()
        self.fit = None


        # Initializing the heap
        self.generateMemoryEntries(INITIAL_MEM_COUNT)
        
        # Assigning Placeholder
        self.memory[0].value = getHexStringFromDecimal(PLACEHOLDER_VALUE)
        self.memory[0].type = MEM_ENT_TYPE_PLACEHOLDER
        self.memory[-1].value = getHexStringFromDecimal(PLACEHOLDER_VALUE)
        self.memory[-1].type = MEM_ENT_TYPE_PLACEHOLDER

        # Add Header and Footer
        # header = Total Bytes - (Count of Placeholder)*Word Size
        header = (INITIAL_MEM_COUNT * WORD_SIZE) - (2*WORD_SIZE)
        self.memory[1].value = getHexStringFromDecimal(header)
        self.memory[-2].value = getHexStringFromDecimal(header)


    def __str__(self) -> str:
        return self.printHeap()

    def printHeap(self) -> str:
        res = ""
        for mem_entry in self.memory:
            res += str(mem_entry.line) + ", "
            if mem_entry.value is not None:
                res += str(mem_entry.value)
            res += "\n"
        
        return res
   

    def my_allocate(self, size, addr_alias):
        addr = self.free_list.allocate(size)
        self.address_mapper[addr_alias] = addr


    def my_reallocate(self, size, old_addr_alias, new_addr_alias):
        new_addr = self.free_list.reallocate(size, old_addr_alias)
        self.address_mapper[new_addr_alias] = new_addr

    def my_free(self, ptr):
        self.free_list.free(ptr)
        del self.address_mapper[ptr]

    def generateMemoryEntries(self, size):
        for i in range(size):
            new_mem = MemoryEntry(self.mem_count, MEM_ENT_TYPE_EMPTY, None)
            self.memory.append(new_mem)
            self.mem_count += 1

    def getFooterLocationFromHeaderLocation(self, header_location: int):
        header_val_dec = getDecimalFromHexString(self.memory[header_location].value)
        if header_val_dec%2 != 0:
            header_val_dec -= 1

        footer_location = header_location + (header_val_dec//WORD_SIZE) - 1        
        return footer_location 

    # Some Getters and Setters
    @property
    def free_list(self):
        return self._free_list
    
    @free_list.setter
    def free_list(self, value):
        if isinstance(value, HeapFreeList):
            self._free_list = value
        else:
            raise("Invalid Free List")

class HeapFreeList:
    def __init__(self, heap: Heap) -> None:
        self.heap = heap
        self.fit = FitType(self)

    def allocate(self, allocation_size: int):
        pass

    def reallocate(self, size: int, old_ptr):
        pass

    def free(self, ptr):
        pass

    def sbrk(self, size: int):
        pass

    # @property
    # def fit(self):
    #     return self._fit
    # @fit.setter
    # def fit(self, value):
    #     if isinstance(value, FitType):
    #         self._fit = value
    #     else:
    #         raise("Invalid fit type")


class FreeList_Implicit(HeapFreeList):
    def __init__(self, heap: Heap) -> None:
        super().__init__(heap)
        
    @property
    def fit(self):
        return self._fit
    @fit.setter
    def fit(self, value):
        if isinstance(value, FitType):
            self._fit = value
        else:
            raise("Invalid fit type")


    def allocate(self, allocation_size: int):
        aligned_allocation_size = alignSize(allocation_size)
        
        new_block_header_location = self.fit.findFreeBlockHeader(INITIAL_HEADER_LOCATION, aligned_allocation_size)

        if new_block_header_location == self.heap.mem_count:
            # Not enough space in the heap, so we need to increase the heap
            new_block_header_location = self.sbrk(aligned_allocation_size)


        current_block_size = getDecimalFromHexString(self.heap.memory[new_block_header_location].value)

        
        new_block_header_value_dec = aligned_allocation_size + HF_OVERHEAD

        if current_block_size - new_block_header_value_dec < (HF_OVERHEAD + ALIGNMENT_SIZE):
            # Block size is too small to split. 
            # So we will take the whole block
            new_block_header_value_dec = current_block_size


        # Set Allocation Bit
        new_block_header_value_dec += ALLOCATION_SET_BIT
        
        # Footer 
        new_block_footer_value_dec = new_block_header_value_dec

        self.heap.memory[new_block_header_location].value = getHexStringFromDecimal(new_block_header_value_dec)

        new_block_footer_location = new_block_header_location + ((new_block_header_value_dec-ALLOCATION_SET_BIT)//WORD_SIZE) - 1
        self.heap.memory[new_block_footer_location].value = getHexStringFromDecimal(new_block_footer_value_dec)

        # Now we have to add the new header for the next block (if splitting is possible)
        if current_block_size > (new_block_header_value_dec - ALLOCATION_SET_BIT):
            remaining_block_size = current_block_size - (new_block_header_value_dec - ALLOCATION_SET_BIT)
            self.heap.memory[new_block_footer_location+1].value = getHexStringFromDecimal(remaining_block_size)


            # Footer
            # To Get the footer, we have to move old header size of words from old header location (which is the new header location).
            current_block_footer_location = new_block_header_location + (current_block_size//WORD_SIZE)-1
            self.heap.memory[current_block_footer_location].value = getHexStringFromDecimal(remaining_block_size)

        # Allocation Complete
        # Now return the address to the payload (header + 1)
        return new_block_header_location+1



    def reallocate(self, size: int, old_ptr_alias):
        new_block_payload_location = self.allocate(size)
        new_block_header_location = new_block_payload_location - 1
        # Now we have to copy the payload of the old block to the new block
        old_block_header_location = self.heap.address_mapper[old_ptr_alias] - 1
        
        old_block_footer_location = self.heap.getFooterLocationFromHeaderLocation(old_block_header_location)
        for i in range(old_block_header_location+1, old_block_footer_location):
            old_payload_mem_ent = self.heap.memory[i]
            
            new_payload_location =  new_block_header_location + (i - old_block_header_location)
            new_payload_mem_ent = self.heap.memory[new_payload_location]
            new_payload_mem_ent.value = old_payload_mem_ent.value

        # Free the old block
        self.free(old_ptr_alias)
        return new_block_payload_location

    def free(self, ptr):
        free_block_header_location = self.heap.address_mapper[ptr] - 1

        free_block_header = self.heap.memory[free_block_header_location]

        # To free the block we have to set the to 0
        free_block_header_value_dec =  getDecimalFromHexString(free_block_header.value) - ALLOCATION_SET_BIT

        # Footer 
        free_block_footer_location = free_block_header_location + (free_block_header_value_dec//WORD_SIZE) - 1
        free_block_footer = self.heap.memory[free_block_footer_location]
        free_block_footer_value_dec = getDecimalFromHexString(free_block_footer.value)

        # Coalesce
        if self.heap.memory[free_block_header_location - 1].type != MEM_ENT_TYPE_PLACEHOLDER:
            # If it's not the first header, we check to coalesce with the previous block
            # In that case, the previous memory entry is a footer. 

            prev_footer_value_dec = getDecimalFromHexString(self.heap.memory[free_block_header_location - 1].value) 
            if prev_footer_value_dec % 2 == 0:
                # The footer of the previous block is divisible by 2
                # Which means it's free
                # So we need to coalesce
                
                # Changing the header to the prev block
                free_block_header_location = free_block_header_location - (prev_footer_value_dec//WORD_SIZE)

                # Get the new block size by adding the two
                free_block_header_value_dec = free_block_header_value_dec + prev_footer_value_dec

        if self.heap.memory[free_block_footer_location + 1].type != MEM_ENT_TYPE_PLACEHOLDER:
            # If it's not the last free block

            # The next memory entry is a header
            next_header_value_dec = getDecimalFromHexString(self.heap.memory[free_block_footer_location+1].value)
            if next_header_value_dec % 2 == 0:
                # It's free if divisible by 2 
                # So Coalesce

                free_block_footer_location = free_block_footer_location + (next_header_value_dec // WORD_SIZE)

                # Add the two headers
                free_block_header_value_dec = free_block_header_value_dec + next_header_value_dec


        # Update the final header and footer values
        self.heap.memory[free_block_header_location].value = getHexStringFromDecimal(free_block_header_value_dec)
        self.heap.memory[free_block_footer_location].value = getHexStringFromDecimal(free_block_header_value_dec)        


    def sbrk(self, size: int):
        # Add memory entries to the heap
        new_block_header_value_dec = size + HF_OVERHEAD
        additional_mem_entries = new_block_header_value_dec//4

        new_mem_count = self.heap.mem_count + additional_mem_entries

        if new_mem_count > MAX_HEAP_SIZE:
            print(f"memory-simulator: total heap capacity reached! ({MAX_HEAP_SIZE} words)")
            exit()     


        for i in range(self.heap.mem_count, new_mem_count):
           new_mem_ent = MemoryEntry(i, MEM_ENT_TYPE_EMPTY, None)
           self.heap.memory.append(new_mem_ent)

        # New block's header will be the last mem_entry of the old size
        new_block_header_location = self.heap.mem_count - 1
        self.heap.mem_count = new_mem_count

       
       
        # Set the new Header Location correctly
        self.heap.memory[new_block_header_location].type = MEM_ENT_TYPE_HEADER
        self.heap.memory[new_block_header_location].value = getHexStringFromDecimal(new_block_header_value_dec)

        # We are not setting the Footer because, since size increased based on requirements, 
        # the footer will be automatically set by the allocator
        
        # Chaning the last placeholder to the new placeholder
        self.heap.memory[new_mem_count - 1].value = getHexStringFromDecimal(PLACEHOLDER_VALUE)
        self.heap.memory[new_mem_count - 1].type = MEM_ENT_TYPE_PLACEHOLDER

        return new_block_header_location



class FreeList_Explicit(HeapFreeList):
    def __init__(self, heap: Heap) -> None:
        super().__init__(heap)
        self.root: str = INITIAL_HEADER_LOCATION

        self.heap.memory[INITIAL_HEADER_LOCATION+PREV_PTR_OFFSET].value = getHexStringFromDecimal(NONE_LOCATION)
        self.heap.memory[INITIAL_HEADER_LOCATION+NEXT_PTR_OFFSET].value = getHexStringFromDecimal(NONE_LOCATION)

    def allocate(self, allocation_size: int):
        aligned_allocation_size = alignSize(allocation_size)

        new_block_header_location = self.fit.findFreeBlockHeader(INITIAL_HEADER_LOCATION, aligned_allocation_size)
        current_block_size = getDecimalFromHexString(self.heap.memory[new_block_header_location].value)

        new_block_header_value_dec = aligned_allocation_size + HF_OVERHEAD
        if current_block_size - new_block_header_value_dec < (HF_OVERHEAD + ALIGNMENT_SIZE):
            # Block size is too small to split.
            # So we will take the whole block
            new_block_header_value_dec = current_block_size

        # Set Allocation Bit
        new_block_header_value_dec += ALLOCATION_SET_BIT
        self.heap.memory[new_block_header_location].value = getHexStringFromDecimal(new_block_header_value_dec)
        
        # Footer
        new_block_footer_value_dec = new_block_header_value_dec
        new_block_footer_location = new_block_header_location + ((new_block_header_value_dec - ALLOCATION_SET_BIT)//WORD_SIZE) - 1
        self.heap.memory[new_block_footer_location].value = getHexStringFromDecimal(new_block_footer_value_dec)


        # Next block Header
        next_block_header_location = getDecimalFromHexString(self.heap.memory[new_block_header_location+NEXT_PTR_OFFSET].value)
        prev_block_header_location = getDecimalFromHexString(self.heap.memory[new_block_header_location+PREV_PTR_OFFSET].value)
        is_prev_block_root = False

        if prev_block_header_location == 0:
            prev_block_header_location = self.root
            is_prev_block_root = True
        

        # If there was a split, we have add the new header of the next block
        if current_block_size > (new_block_header_value_dec - ALLOCATION_SET_BIT):
            split_block_size = current_block_size - (new_block_header_value_dec - ALLOCATION_SET_BIT)

            split_block_header_loaction = new_block_footer_location + 1
            self.heap.memory[split_block_header_loaction].value = getHexStringFromDecimal(split_block_size)

            # Footer of the new splitted block
            split_block_footer_location = split_block_header_loaction+(split_block_size//WORD_SIZE)-1
            self.heap.memory[split_block_footer_location].value = getHexStringFromDecimal(split_block_size)

            # Update the pointers of the Free list
                
            # Split block pointers
            self.heap.memory[split_block_header_loaction+PREV_PTR_OFFSET].value = getHexStringFromDecimal(prev_block_header_location)
            self.heap.memory[split_block_header_loaction+NEXT_PTR_OFFSET].value = getHexStringFromDecimal(next_block_header_location)

            
            if next_block_header_location != 0: 
                # if there is a next block
                # Next block's Previous pointer is set to split block's header
                self.heap.memory[next_block_header_location+PREV_PTR_OFFSET].value = getHexStringFromDecimal(split_block_header_loaction)

            # Prev Block's Next Pointer
            if not is_prev_block_root:
                self.heap.memory[prev_block_header_location+NEXT_PTR_OFFSET].value = getHexStringFromDecimal(split_block_header_loaction)
                
            if is_prev_block_root: 
                # Set Root pointing to current header
                self.root = split_block_header_loaction
                self.heap.memory[split_block_header_loaction+PREV_PTR_OFFSET].value = getHexStringFromDecimal(NONE_LOCATION)
        else:
            # Setting Pointers (no split)
            # my_prev.next = my_next
            self.heap.memory[prev_block_header_location+NEXT_PTR_OFFSET].value = getHexStringFromDecimal(next_block_header_location)

            # my_next.prev = my_prev
            self.heap.memory[next_block_header_location+PREV_PTR_OFFSET].value = getHexStringFromDecimal(prev_block_header_location)

            if is_prev_block_root:
                self.root = next_block_header_location
                self.heap.memory[next_block_header_location+PREV_PTR_OFFSET].value = getHexStringFromDecimal(NONE_LOCATION)


        return new_block_header_location+1
    
    def free(self, ptr):
        # Get the Header from the alias ptr
        free_block_header_location = self.heap.address_mapper[ptr]-1 
        # Free the allocation 
        free_block_header_val_dec = getDecimalFromHexString(self.heap.memory[free_block_header_location].value) - ALLOCATION_SET_BIT


        # Footer
        free_block_footer_location = free_block_header_location + (free_block_header_val_dec//WORD_SIZE) - 1
        free_block_footer_value_dec = free_block_header_val_dec

        # Coalesce
        if self.heap.memory[free_block_header_location-1].type != MEM_ENT_TYPE_PLACEHOLDER:
            # It's not the direct next block of the placeholder.
            # Meaning there is a possibility of coalescing of previous block
            prev_block_footer_value_dec = getDecimalFromHexString(self.heap.memory[free_block_header_location - 1].value)
            if prev_block_footer_value_dec % 2 == 0:
                # Prev block is free
                # We have to adjust the pointers of the previous block before coalescing
                # Get the location of prev and next block
                my_block_footer_location = free_block_header_location-1
                my_block_header_location = my_block_footer_location - (prev_block_footer_value_dec//WORD_SIZE) + 1
                my_prev_location = getDecimalFromHexString(self.heap.memory[my_block_header_location+PREV_PTR_OFFSET].value)
                my_next_location = getDecimalFromHexString(self.heap.memory[my_block_header_location+NEXT_PTR_OFFSET].value)
                
                # my_prev.next = my_next
                if my_prev_location == 0:
                    # the prev block is the root
                    self.root = my_next_location 
                else:
                    self.heap.memory[my_prev_location+NEXT_PTR_OFFSET].value = getHexStringFromDecimal(my_next_location)

                # my_next.prev = my_prev
                if my_next_location != 0:
                    self.heap.memory[my_next_location+PREV_PTR_OFFSET].value = getHexStringFromDecimal(my_prev_location)

                # Now coalesce the header
                free_block_header_location = free_block_header_location - (prev_block_footer_value_dec//WORD_SIZE)
                # New block size
                free_block_header_val_dec = free_block_header_val_dec + prev_block_footer_value_dec

        next_location_zero = False

        if self.heap.memory[free_block_footer_location + 1].type != MEM_ENT_TYPE_PLACEHOLDER:
            # It's not the last block

            next_block_header_location = free_block_footer_location + 1
            next_block_header_val_dec = getDecimalFromHexString(self.heap.memory[next_block_header_location].value)

            if next_block_header_val_dec % 2 == 0:
                # Next block is free
                
                # We have to adjust the pointers of the previous block before coalescing
                # Get the location of prev and next block
                my_block_header_location = next_block_header_location
                my_prev_location = getDecimalFromHexString(self.heap.memory[my_block_header_location+PREV_PTR_OFFSET].value)
                my_next_location = getDecimalFromHexString(self.heap.memory[my_block_header_location+NEXT_PTR_OFFSET].value)
                
                # my_prev.next = my_next
                if my_prev_location == 0:
                    # the prev block is the root
                    if my_next_location != 0:
                        self.root = my_next_location
                    else:
                        self.root = free_block_header_location
                else:
                    self.heap.memory[my_prev_location+NEXT_PTR_OFFSET].value = getHexStringFromDecimal(my_next_location)

                # my_next.prev = my_prev
                # if my_next_location != 0:
                    # self.heap.memory[my_next_location+PREV_PTR_OFFSET].value = getHexStringFromDecimal(my_prev_location)
                if my_next_location == 0:
                    next_location_zero = True



                free_block_footer_location += (next_block_header_val_dec//WORD_SIZE)
                free_block_header_val_dec += next_block_header_val_dec


        # LIFO policy
        # Current Top Block
        current_top_block_location = self.root
        
        # set root to the Freed block
        self.root = free_block_header_location
        # Free block's prev = none
        self.heap.memory[free_block_header_location + PREV_PTR_OFFSET].value = getHexStringFromDecimal(NONE_LOCATION)
        if current_top_block_location != free_block_header_location:
            # Free block.next = current top block
            self.heap.memory[free_block_header_location + NEXT_PTR_OFFSET].value = getHexStringFromDecimal(current_top_block_location)
            # CurrentTopBlock.prev = FreeBlockHeader
            self.heap.memory[current_top_block_location + PREV_PTR_OFFSET].value = getHexStringFromDecimal(free_block_header_location)

        else:
            self.heap.memory[free_block_header_location+NEXT_PTR_OFFSET].value = getHexStringFromDecimal(NONE_LOCATION) 

        # Setting header and footer of the freed block
        self.heap.memory[free_block_header_location].value = getHexStringFromDecimal(free_block_header_val_dec)
        self.heap.memory[free_block_footer_location].value = getHexStringFromDecimal(free_block_header_val_dec)

    def reallocate(self, size: int, old_ptr_alias):
        new_block_payload_location = self.allocate(size)
        new_block_header_location = new_block_payload_location - 1
        # Now we have to copy the payload of the old block to the new block
        old_block_header_location = self.heap.address_mapper[old_ptr_alias] - 1
        
        old_block_footer_location = self.heap.getFooterLocationFromHeaderLocation(old_block_header_location)
        for i in range(old_block_header_location+1, old_block_footer_location):
            old_payload_mem_ent = self.heap.memory[i]
            
            new_payload_location =  new_block_header_location + (i - old_block_header_location)
            new_payload_mem_ent = self.heap.memory[new_payload_location]
            new_payload_mem_ent.value = old_payload_mem_ent.value

        # Free the old block
        self.free(old_ptr_alias)
        return new_block_payload_location


    @property
    def fit(self):
        return self._fit
    @fit.setter
    def fit(self, value):
        if isinstance(value, FitType):
            self._fit = value
        else:
            raise("Invalid fit type")


class FitType:
    def __init__(self, free_list: HeapFreeList) -> None:
        self.free_list = free_list

    def findFreeBlockHeader(self, start_index: int, new_block_size: int) -> int:
        pass

class FitType_FirstFitImplicit(FitType):
    def __init__(self, free_list: HeapFreeList) -> None:
        super().__init__(free_list)

    def findFreeBlockHeader(self, start_index: int, new_block_size: int) -> int:
        i = start_index
        while i < self.free_list.heap.mem_count - 1:
            block_size = getDecimalFromHexString(self.free_list.heap.memory[i].value)
            if (block_size % 2 == 0) and (block_size >= (new_block_size + HF_OVERHEAD)):
                return i
            i += block_size//WORD_SIZE

        # Returning mem_count which is invalid to indicate no free blocks found
        return self.free_list.heap.mem_count
    
class FitType_BestFitImplicti(FitType):
    def __init__(self, free_list: HeapFreeList) -> None:
        super().__init__(free_list)

    def findFreeBlockHeader(self, start_index: int, new_block_size: int) -> int:
        i = start_index

        # Setting min to highest value possible
        min_block_location = self.free_list.heap.mem_count
        min_block_size = self.free_list.heap.mem_count * WORD_SIZE
        while i < self.free_list.heap.mem_count-1:
            block_size = getDecimalFromHexString(self.free_list.heap.memory[i].value)
            if (block_size % 2 == 0) and (block_size >= new_block_size + HF_OVERHEAD):
                if block_size < min_block_size:
                    min_block_size = block_size
                    min_block_location = i

            i += block_size//WORD_SIZE

        return min_block_location
           
           
class FitType_FirstFitExplicit(FitType):
    def __init__(self, free_list: FreeList_Explicit) -> None:
        super().__init__(free_list)  
    
    def findFreeBlockHeader(self, start_index: int, new_block_size: int) -> int:
        curr_block_header_location = self.free_list.root

        while curr_block_header_location != 0:
            curr_block_size = getDecimalFromHexString(self.free_list.heap.memory[curr_block_header_location].value)
            if curr_block_size >= (new_block_size + HF_OVERHEAD):
                return curr_block_header_location

            next_ptr_location = curr_block_header_location + NEXT_PTR_OFFSET
            curr_block_header_location = getDecimalFromHexString(self.free_list.heap.memory[next_ptr_location].value) 

class FitType_BestFitExplicit(FitType):
    def __init__(self, free_list: FreeList_Explicit) -> None:
        super().__init__(free_list)
    
    def findFreeBlockHeader(self, start_index: int, new_block_size: int) -> int:
        curr_block_header_location = self.free_list.root

        
        min_block_size = self.free_list.heap.mem_count*WORD_SIZE
        min_block_header_loaction = self.free_list.heap.mem_count
        while curr_block_header_location != 0:
            curr_block_size = getDecimalFromHexString(self.free_list.heap.memory[curr_block_header_location].value)
            if curr_block_size >= (new_block_size + HF_OVERHEAD):
                if curr_block_header_location < min_block_size:
                    min_block_size = curr_block_size
                    min_block_header_loaction = curr_block_header_location

            next_ptr_location = curr_block_header_location + NEXT_PTR_OFFSET
            curr_block_header_location = getDecimalFromHexString(self.free_list.heap.memory[next_ptr_location].value) 

        return min_block_header_loaction


def main():
    argv = sys.argv

    arguements = {
        ARGUMENT_VERBOSE: False,
        ARGUMENT_OUTPUT: "output.txt",
        ARGUMENT_FREE_LIST: None,
        ARGUMENT_FIT: None,
        ARGUMENT_INPUT: None
    }


    if len(argv) > 7:
        printError()
        return -1

    i = 1
    while i < len(argv):
        if argv[i] == '-v':
            arguements[ARGUMENT_VERBOSE] = True
        elif argv[i] == '-o':
            if os.path.isdir(argv[i]):
                error_msg = "Invalid output file"
                printError(error_msg)
                return -1
            
            arguements[ARGUMENT_OUTPUT] = argv[i+1]
            i+=1

        elif argv[i].startswith("--free-list"):
            tmp = argv[i].split("=")
            if tmp[1] == "implicit":
                arguements[ARGUMENT_FREE_LIST] = ARG_VAL_IMPLICIT_LIST
            elif tmp[1] == "explicit":
                arguements[ARGUMENT_FREE_LIST] = ARG_VAL_EXPLICIT_LIST
            else:
                error_msg = "Invalid free list."
                printError(error_msg)
                return -1

        elif argv[i].startswith("--fit"):
            tmp = argv[i].split("=")
            if tmp[1] == "first":
                arguements[ARGUMENT_FIT] = ARG_VAL_FIRST_FIT
            elif tmp[1] == "best":    
                arguements[ARGUMENT_FIT] = ARG_VAL_BEST_FIT
            else:
                error_msg = "Invalid fit type."
                printError(error_msg)
                return -1
        elif os.path.isfile(argv[i]):
            arguements[ARGUMENT_INPUT] = argv[i]
        else:
            error_msg = "Invalid input file."
            printError(error_msg)
            return -1
        
        i += 1

    if arguements[ARGUMENT_INPUT] is None \
        or arguements[ARGUMENT_FIT] is None \
        or arguements[ARGUMENT_FREE_LIST] is None:
        printError()
        return -1

    heap = Heap()
    heap.fit = arguements[ARGUMENT_FIT]
    

    if arguements[ARGUMENT_FREE_LIST] == ARG_VAL_IMPLICIT_LIST:
        heap.free_list = FreeList_Implicit(heap)

        if arguements[ARGUMENT_FIT] == ARG_VAL_FIRST_FIT:
            heap.free_list.fit = FitType_FirstFitImplicit(heap.free_list)
        elif arguements[ARGUMENT_FIT] == ARG_VAL_BEST_FIT:
            heap.free_list.fit = FitType_BestFitImplicti(heap.free_list)

    elif arguements[ARGUMENT_FREE_LIST] == ARG_VAL_EXPLICIT_LIST:
        heap.free_list = FreeList_Explicit(heap)
        if arguements[ARGUMENT_FIT] == ARG_VAL_FIRST_FIT:
            heap.free_list.fit = FitType_FirstFitExplicit(heap.free_list)
        elif arguements[ARGUMENT_FIT] == ARG_VAL_BEST_FIT:
            heap.free_list.fit = FitType_BestFitExplicit(heap.free_list)


    # Open the Input File
    with open(arguements[ARGUMENT_INPUT], 'r') as input_file:
        for line in input_file:
            cmd = line.replace("\n", '').replace(",", "").split(" ")

            # Converting all elements to int except for the first one
            for i in range(len(cmd)):
                if i != 0:
                    cmd[i] = int(cmd[i])


            if cmd[CMD_IND_OPERATION] == "a":
                heap.my_allocate((cmd[CMD_A_IND_SIZE]), cmd[CMD_A_IND_ADDR])
            elif cmd[CMD_IND_OPERATION] == "r":
                heap.my_reallocate((cmd[CMD_R_IND_SIZE]), cmd[CMD_R_IND_OLD_ADDR], cmd[CMD_R_IND_NEW_ADDR])
            elif cmd[CMD_IND_OPERATION] == "f":
                heap.my_free(cmd[CMD_F_IND_ADDR])

    
    # Writing to Output file
    with open(arguements[ARGUMENT_OUTPUT], 'w') as outfile:
        outfile.write(heap.printHeap())



if __name__ == "__main__":
    main()