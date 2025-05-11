import os
import re
import shutil

def read_readme():
    """README_en.md 파일을 읽고 카테고리와 항목 목록을 추출합니다."""
    categories = []
    current_category = None
    items_in_category = []
    
    with open('README_en.md', 'r', encoding='utf-8') as file:
        content = file.read()
        
    # 카테고리 섹션 찾기
    category_section = re.search(r'## Categories & Template List\s+(.*?)---', content, re.DOTALL)
    if not category_section:
        print("카테고리 섹션을 찾을 수 없습니다.")
        return []
    
    category_content = category_section.group(1)
    
    # 각 카테고리와 항목 추출
    category_pattern = r'### (\d+)_\*\*(.*?)\*\*|\### (\d+)_(.*?)\n'
    item_pattern = r'- (.*?)(?:\n|$)'
    
    current_pos = 0
    while current_pos < len(category_content):
        # 카테고리 찾기
        category_match = re.search(category_pattern, category_content[current_pos:], re.DOTALL)
        if not category_match:
            break
            
        # 카테고리 정보 추출
        if category_match.group(1) and category_match.group(2):
            category_num = category_match.group(1)
            category_name = category_match.group(2)
        else:
            category_num = category_match.group(3)
            category_name = category_match.group(4)
            
        folder_name = f"{category_num}_{category_name}"
        
        # 현재 위치 업데이트
        current_pos += category_match.start() + len(category_match.group(0))
        
        # 다음 카테고리 또는 문서 끝까지의 내용 추출
        next_category_match = re.search(category_pattern, category_content[current_pos:], re.DOTALL)
        if next_category_match:
            end_pos = current_pos + next_category_match.start()
            category_items_content = category_content[current_pos:end_pos]
        else:
            category_items_content = category_content[current_pos:]
        
        # 항목 추출
        items = re.findall(item_pattern, category_items_content)
        
        categories.append({
            'number': category_num,
            'name': folder_name,
            'items': items
        })
    
    return categories

def find_matching_files(item_name, tasks_dir):
    """tasks 폴더에서 항목 이름과 일치하는 파일을 찾습니다."""
    matching_files = []
    
    # 특수 문자 처리
    item_name_escaped = re.escape(item_name)
    # 따옴표와 같은 특수 문자 처리
    item_name_escaped = item_name_escaped.replace("\\'", "['']").replace('\\"', '[""]')
    
    pattern = re.compile(f"^{item_name_escaped}\\.(json|txt)$", re.IGNORECASE)
    
    for filename in os.listdir(tasks_dir):
        if pattern.match(filename) or item_name.lower() in filename.lower():
            matching_files.append(filename)
    
    return matching_files

def move_files():
    """파일을 카테고리 폴더로 이동하고 넘버링합니다."""
    categories = read_readme()
    tasks_dir = 'tasks'
    
    for category in categories:
        category_folder = category['name']
        category_num = category['number']
        
        print(f"처리 중: {category_folder}")
        
        # 각 항목 처리
        for i, item in enumerate(category['items'], 1):
            item_num = f"{category_num}_{i}"
            
            # 일치하는 파일 찾기
            matching_files = find_matching_files(item, tasks_dir)
            
            for file in matching_files:
                file_name, file_ext = os.path.splitext(file)
                new_filename = f"{item_num}_{file_name}{file_ext}"
                
                # 파일 복사
                src_path = os.path.join(tasks_dir, file)
                dst_path = os.path.join(category_folder, new_filename)
                
                try:
                    shutil.copy2(src_path, dst_path)
                    print(f"  복사됨: {file} -> {new_filename}")
                    # 복사 성공 후 원본 파일 삭제
                    os.remove(src_path)
                    print(f"  삭제됨: {file} (tasks 폴더에서)")
                except Exception as e:
                    print(f"  오류: {file} 처리 실패 - {str(e)}")

if __name__ == "__main__":
    move_files()
