#!/usr/bin/env python3
import argparse
import glob
import os
import subprocess
import time
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="JSON 파일들을 실행합니다.")
    parser.add_argument("--model", type=str, default="grok-3-mini-beta", help="사용할 모델 (기본값: grok-3-mini-beta)")
    parser.add_argument("--provider", type=str, default="xai", help="사용할 제공자 (기본값: xai)")
    parser.add_argument("--task-dir", type=str, default="tasks", help="작업 파일들이 위치한 디렉토리 (기본값: tasks)")
    parser.add_argument(
        "--output", type=str, default="run_tasks.sh", help="명령어를 저장할 쉘 스크립트 파일 (기본값: run_tasks.sh)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="실제로 쉘 스크립트를 생성하지 않고 명령어만 출력합니다."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # 모든 JSON 파일 찾기
    task_dir = Path(args.task_dir)
    json_files = list(task_dir.glob("*.json"))

    if not json_files:
        print(f"'{args.task_dir}' 디렉토리에 JSON 파일이 없습니다.")
        return

    print(f"'{args.task_dir}' 디렉토리에서 {len(json_files)}개의 JSON 파일을 찾았습니다.")

    # 출력 파일 생성
    if not args.dry_run:
        output_file = Path(args.output)
        with open(output_file, "w") as f:
            f.write("#!/bin/bash\n\n")
            f.write("# 자동 생성된 작업 실행 스크립트\n")
            f.write(f"# 생성 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 모델: {args.model}\n")
            f.write(f"# 제공자: {args.provider}\n\n")

            # 각 파일에 대해 명령어 작성
            for i, json_file in enumerate(json_files, 1):
                file_path = str(json_file)
                cmd = f'clear && python scripts/cli.py run --file="{file_path}" --model={args.model} --provider={args.provider}'

                # f.write(f'echo "[{i}/{len(json_files)}] 실행 중: {file_path}"\n')
                f.write(f"{cmd}\n\n")

                # 사용자가 진행 상황을 볼 수 있도록 현재 진행 중인 작업 출력
                print(f"[{i}/{len(json_files)}] 추가됨: {file_path}")

        # 스크립트 실행 권한 설정
        os.chmod(output_file, 0o755)
        print(f"\n쉘 스크립트가 '{args.output}'에 생성되었습니다.")
        print(f"다음 명령어로 실행하세요: ./{args.output}")
    else:
        # 각 파일에 대해 명령어 출력 (dry-run 모드)
        for i, json_file in enumerate(json_files, 1):
            file_path = str(json_file)
            cmd = f'clear && python scripts/cli.py run --file="{file_path}" --model={args.model} --provider={args.provider}'

            print(f"\n[{i}/{len(json_files)}] 명령어: {cmd}")


if __name__ == "__main__":
    main()
