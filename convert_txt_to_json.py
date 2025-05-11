import os
import json
import re

def convert_txt_to_json(input_dir, output_dir=None):
    """
    tasks_original 디렉토리에 있는 모든 txt 파일을 읽어서 json 파일로 변환합니다.
    
    Args:
        input_dir (str): txt 파일이 있는 디렉토리 경로
        output_dir (str, optional): json 파일을 저장할 디렉토리 경로. 기본값은 None으로, 
                                   이 경우 input_dir과 동일한 디렉토리에 저장됩니다.
    """
    # 출력 디렉토리가 지정되지 않은 경우 입력 디렉토리와 동일하게 설정
    if output_dir is None:
        output_dir = input_dir
    
    # 출력 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 입력 디렉토리의 모든 파일 목록 가져오기
    files = os.listdir(input_dir)
    
    # txt 파일만 필터링
    txt_files = [f for f in files if f.endswith('.txt')]
    
    print(f"총 {len(txt_files)}개의 txt 파일을 변환합니다.")
    
    success_count = 0
    error_count = 0
    
    for txt_file in txt_files:
        try:
            # 파일 경로 설정
            txt_path = os.path.join(input_dir, txt_file)
            json_file = txt_file.replace('.txt', '.json')
            json_path = os.path.join(output_dir, json_file)
            
            # txt 파일 읽기
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # JSON 부분 추출 (파일 끝에 추가 텍스트가 있을 수 있음)
            # JSON 객체는 중괄호({})로 시작하고 끝나므로, 이를 기준으로 추출
            json_match = re.search(r'({.*})', content, re.DOTALL)
            
            if json_match:
                json_content = json_match.group(1)
                
                # JSON 파싱하여 유효성 검사
                json_obj = json.loads(json_content)
                
                # JSON 파일로 저장
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_obj, f, ensure_ascii=False, indent=2)
                
                success_count += 1
                print(f"변환 성공: {txt_file} -> {json_file}")
            else:
                print(f"JSON 형식을 찾을 수 없음: {txt_file}")
                error_count += 1
                
        except Exception as e:
            print(f"변환 실패: {txt_file} - 오류: {str(e)}")
            error_count += 1
    
    print(f"\n변환 완료: 성공 {success_count}개, 실패 {error_count}개")

if __name__ == "__main__":
    # tasks_original 디렉토리의 txt 파일을 같은 디렉토리에 json 파일로 변환
    input_directory = "tasks_original"
    output_directory = "tasks_original"
    
    convert_txt_to_json(input_directory, output_directory)
