import PyPDF2
MAX_TEXT_LENGTH = 10000
def extract_text(file_path: str) -> str:
    """
    从文件中提取文本。
    支持从PDF文件中提取文本内容，并进行换行优化处理。
    
    Args:
        file_path: PDF文件路径
        
    Returns:
        提取的文本内容
    """
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()[:MAX_TEXT_LENGTH]
    else:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
            
            # 提取所有页面的文本
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                
                # 处理假换行：
                # 1. 分割成行
                lines = text.split('\n')
                # 2. 处理每一行
                for i, line in enumerate(lines):
                    # 如果行不是空的，且不以句号、问号、感叹号结尾，且不是最后一行
                    if (line.strip() and i < len(lines) - 1 and 
                        not line.strip().endswith(('.', '?', '!', '。', '？', '！'))):
                        # 添加空格而不是换行
                        lines[i] = line.strip() + ' '
                    else:
                        lines[i] = line.strip()
                
                text_parts.append(''.join(lines))
            
            return ('\n'.join(text_parts)).strip()[:MAX_TEXT_LENGTH]
            
        except Exception as e:
            print(f"提取PDF文本时发生错误: {str(e)}")
            return ""
    
if __name__ == "__main__":
    text = extract_text(r"docs/2405.16506v2-GRAG.pdf")
    print(text)
