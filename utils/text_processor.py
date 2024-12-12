def split_text_basic(text: str) -> list[str]:
    """
    将文本分割为段落，每个段落长度不超过500字符。
    """
    return [text[i:i+500] for i in range(0, len(text), 500)]

def split_text_recursive(text: str, max_chunk_size: int = 500, min_chunk_size: int = 100) -> list[str]:
    """
    将文本分割为段落，每个段落长度在min_chunk_size和max_chunk_size之间。
    使用递归方式进行切割，优先保持语义完整性。
    """
    # 如果文本长度小于最大块大小，直接返回
    if len(text) <= max_chunk_size:
        return [text]
    
    # 定义分隔符优先级
    separators = [
        '\n\n',  # 段落分隔符
        # '\n',    # 换行符:先取消，有时候会导致连词符号两边被截断
        ['。', '？', '?', '！', '!', '...', '…'],  # 句子终止符
        ['，', ',', '；', ';', '：', ':']  # 其他标点符号
    ]
    
    for separator in separators:
        chunks = []
        if isinstance(separator, list):
            # 对于标点符号组，找到文本中出现的所有分隔位置
            positions = []
            for sep in separator:
                pos = 0
                while True:
                    pos = text.find(sep, pos)
                    if pos == -1:
                        break
                    positions.append(pos + len(sep))
                    pos += len(sep)
            positions.sort()
            
            if positions:
                current_pos = 0
                current_chunk = ""
                for pos in positions:
                    if len(current_chunk) + (pos - current_pos) > max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = text[current_pos:pos]
                    else:
                        current_chunk += text[current_pos:pos]
                    current_pos = pos
                if current_pos < len(text):
                    chunks.append(current_chunk + text[current_pos:])
        else:
            # 对于简单分隔符（如换行符），直接分割
            temp_chunks = text.split(separator)
            current_chunk = ""
            
            for chunk in temp_chunks:
                if not chunk.strip():
                    continue
                if len(current_chunk) + len(chunk) + len(separator) <= max_chunk_size:
                    current_chunk += (separator if current_chunk else "") + chunk
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = chunk
            if current_chunk:
                chunks.append(current_chunk)
        
        # 如果找到了合适的分割方式，进行递归处理
        if len(chunks) > 1:
            result = []
            for chunk in chunks:
                if len(chunk) > max_chunk_size:
                    result.extend(split_text_recursive(chunk, max_chunk_size, min_chunk_size))
                elif len(chunk) < min_chunk_size and result:
                    # 尝试将过短的块与前一个块合并
                    if len(result[-1]) + len(chunk) <= max_chunk_size:
                        result[-1] += chunk
                    else:
                        result.append(chunk)
                else:
                    result.append(chunk)
            return result
    
    # 如果没有找到合适的分隔符，则按最大块大小强制分割
    return split_text_basic(text)

def split_text_by_sentence(text: str, max_chunk_size: int = 500, min_chunk_size: int = 100) -> list[str]:
    """
    将文本分割为chunks：
    1. 首先按段落（\n\n）分割
    2. 对于超过max_chunk_size的段落，按句子分割（。？!...等）
    3. 将句子逐个添加到chunk中，直到达到max_chunk_size或段落结束
    4. 尽量保持每个chunk的长度在min_chunk_size和max_chunk_size之间
    """
    # 句子结束符
    sentence_ends = ['。', '？', '?', '！', '!', '...', '…']
    # 常见的缩写词列表
    abbreviations = ['Mr.', 'Mrs.', 'Dr.', 'Prof.', 'Sr.', 'Jr.', 'vs.', 'etc.', 'e.g.', 'i.e.']
    
    def is_sentence_end(text: str, pos: int) -> bool:
        """判断当前位置的点号是否是句子结尾"""
        if pos == -1 or pos >= len(text):
            return False
            
        # 如果是其他明确的句子结束符，直接返回True
        if text[pos] in ['。', '？', '?', '！', '!']:
            return True
            
        if text[pos] != '.':
            return False
            
        # 检查是否是小数点（前后都是数字）
        if pos > 0 and pos < len(text) - 1:
            if text[pos-1].isdigit() and text[pos+1].isdigit():
                return False
                
        # 检查是否是缩写词
        for abbr in abbreviations:
            if pos >= len(abbr) - 1:
                if text[pos-len(abbr)+1:pos+1] == abbr:
                    return False
                    
        # 检查句号后是否跟着空格或换行（句子结尾的特征）
        if pos < len(text) - 1:
            return text[pos+1].isspace()
            
        return True
    
    # 先按段落分割
    paragraphs = text.split('\n\n')
    result = []
    
    for para in paragraphs:
        if not para.strip():  # 跳过空段落
            continue
            
        if len(para) <= max_chunk_size and len(para) >= min_chunk_size:
            result.append(para)
            continue
            
        # 找出所有句子结束位置
        positions = []
        pos = 0
        while pos < len(para):
            # 检查常规句子结束符
            found = False
            for sep in sentence_ends:
                if para.startswith(sep, pos):
                    positions.append(pos + len(sep))
                    pos += len(sep)
                    found = True
                    break
            
            # 检查英文句号
            if not found and para[pos] == '.' and is_sentence_end(para, pos):
                positions.append(pos + 1)
                
            pos += 1 if not found else 0
        
        # 如果没找到任何句子分隔符，直接添加整段
        if not positions:
            result.append(para)
            continue
            
        # 按句子组合chunks
        current_chunk = ""
        last_pos = 0
        
        for pos in positions:
            sentence = para[last_pos:pos]
            # 如果加入当前句子会超过最大长度，先保存当前chunk
            if len(current_chunk) + len(sentence) > max_chunk_size:
                if current_chunk and len(current_chunk) >= min_chunk_size:
                    result.append(current_chunk)
                    current_chunk = sentence
                else:
                    # 如果当前chunk太短，继续添加句子
                    current_chunk += sentence
            else:
                current_chunk += sentence
            last_pos = pos
        
        # 处理最后一个chunk
        if last_pos < len(para):
            remaining = para[last_pos:]
            if len(current_chunk) + len(remaining) <= max_chunk_size:
                current_chunk += remaining
            else:
                if current_chunk and len(current_chunk) >= min_chunk_size:
                    result.append(current_chunk)
                result.append(remaining)
        
        if current_chunk and len(current_chunk) >= min_chunk_size:
            result.append(current_chunk)
        elif current_chunk and result:
            # 如果最后一个chunk太短，尝试与前一个chunk合并
            if len(result[-1]) + len(current_chunk) <= max_chunk_size:
                result[-1] += current_chunk
            else:
                result.append(current_chunk)
    
    return result
try:
    import utils.file_processor  as file_processor
except:
    import file_processor
if __name__ == "__main__":
    text = file_processor.extract_text("docs/2405.16506v2-GRAG.pdf")
    
    print("原文：")
    print(text)
    print("分割后：")
    for chunk in split_text_by_sentence(text):
        print("-"*20)
        print(chunk)
        print("-"*20)
