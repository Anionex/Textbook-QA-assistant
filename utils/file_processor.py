import pdfplumber
import chardet

# START_TEXT_LENGTH = 14002
# MAX_TEXT_LENGTH = 200000
START_TEXT_LENGTH = 0
MAX_TEXT_LENGTH = 500000
def extract_text(file_path: str) -> str:
    if file_path.endswith('.txt'):
        with open(file_path, 'rb') as rawfile:
            raw_data = rawfile.read()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']
            
        with open(file_path, 'r', encoding=encoding) as file:
            text = file.read()[START_TEXT_LENGTH:START_TEXT_LENGTH+MAX_TEXT_LENGTH]
            print("text length: ", len(text))
            print("detected encoding: ", encoding)
            return text
        
    else:
        try:
            text_count = 0
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text_count >= START_TEXT_LENGTH + MAX_TEXT_LENGTH:
                        break

                    # 调整文本以从START_TEXT_LENGTH开始
                    if text_count < START_TEXT_LENGTH:
                        if text_count + len(text) < START_TEXT_LENGTH:
                            text_count += len(text)
                            continue
                        else:
                            text = text[START_TEXT_LENGTH - text_count:]
                            text_count = START_TEXT_LENGTH

                    # 处理假换行：
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if (line.strip() and i < len(lines) - 1 and 
                            not line.strip().endswith(('.', '?', '!', '。', '？', '！'))):
                            lines[i] = line.strip() + ' '
                        else:
                            lines[i] = line.strip()
                    
                    text_parts.append(''.join(lines))
                    text_count += len(text)

                    # 如果已经达到所需长度，停止
                    if text_count >= START_TEXT_LENGTH + MAX_TEXT_LENGTH:
                        break
            
            return ('\n'.join(text_parts)).strip()[:MAX_TEXT_LENGTH]
            
        except Exception as e:
            print(f"提取PDF文本时发生错误: {str(e)}")
            return ""
    
if __name__ == "__main__":
    text = extract_text(r"docs/曼昆 经济学原理.txt")
    # print(text)
