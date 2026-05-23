import os
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

INCLUDE_EXTENSIONS = {
    '.py', '.js', '.ts', '.vue', '.jsx', '.tsx',
    '.html', '.css', '.scss', '.less',
    '.java', '.go', '.rs', '.c', '.cpp', '.h', '.hpp',
    '.rb', '.php', '.swift', '.kts'
}

EXCLUDE_DIRS = {
    'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache',
    'logs', 'dist', 'build', '.vscode', '.idea', 'env'
}

EXCLUDE_FILES = {
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Cargo.lock',
    'go.sum', 'composer.lock', 'Gemfile.lock', 'Pipfile.lock'
}

def count_file_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        total = len(lines)
        code = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        blank = sum(1 for line in lines if not line.strip())
        comment = total - code - blank
        return total, code, blank, comment
    except:
        return 0, 0, 0, 0

def scan_directory():
    stats = defaultdict(lambda: {'files': 0, 'total': 0, 'code': 0, 'blank': 0, 'comment': 0})
    category_stats = defaultdict(lambda: {'files': 0, 'total': 0, 'code': 0, 'blank': 0, 'comment': 0})

    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            if filename in EXCLUDE_FILES:
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext not in INCLUDE_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, filename)
            relpath = os.path.relpath(filepath, ROOT_DIR)
            total, code, blank, comment = count_file_lines(filepath)

            stats[ext]['files'] += 1
            stats[ext]['total'] += total
            stats[ext]['code'] += code
            stats[ext]['blank'] += blank
            stats[ext]['comment'] += comment

            if 'backend' in relpath:
                category = 'Backend'
            elif 'frontend' in relpath:
                category = 'Frontend'
            else:
                category = 'Other'
            category_stats[category]['files'] += 1
            category_stats[category]['total'] += total
            category_stats[category]['code'] += code
            category_stats[category]['blank'] += blank
            category_stats[category]['comment'] += comment

    return stats, category_stats

def print_report(stats, category_stats):
    print('=' * 70)
    print(' ' * 15 + '代码统计报告' + ' ' * 15)
    print('=' * 70)

    print('\n【按模块分类】')
    print('-' * 70)
    print(f"{'模块':<15} {'文件数':>8} {'总行数':>10} {'代码行数':>10} {'空行':>8} {'注释行':>8}")
    print('-' * 70)

    total_all = {'files': 0, 'total': 0, 'code': 0, 'blank': 0, 'comment': 0}
    for category in sorted(category_stats.keys()):
        s = category_stats[category]
        print(f"{category:<15} {s['files']:>8} {s['total']:>10} {s['code']:>10} {s['blank']:>8} {s['comment']:>8}")
        for k in total_all:
            total_all[k] += s[k]

    print('-' * 70)
    print(f"{'合计':<15} {total_all['files']:>8} {total_all['total']:>10} {total_all['code']:>10} {total_all['blank']:>8} {total_all['comment']:>8}")

    print('\n【按文件类型分类】')
    print('-' * 70)
    print(f"{'类型':<15} {'文件数':>8} {'总行数':>10} {'代码行数':>10} {'空行':>8} {'注释行':>8}")
    print('-' * 70)

    for ext in sorted(stats.keys(), key=lambda x: stats[x]['total'], reverse=True):
        s = stats[ext]
        print(f"{ext:<15} {s['files']:>8} {s['total']:>10} {s['code']:>10} {s['blank']:>8} {s['comment']:>8}")

    print('-' * 70)
    grand_total = {k: sum(stats[ext][k] for ext in stats) for k in ['files', 'total', 'code', 'blank', 'comment']}
    print(f"{'合计':<15} {grand_total['files']:>8} {grand_total['total']:>10} {grand_total['code']:>10} {grand_total['blank']:>8} {grand_total['comment']:>8}")

    print('\n' + '=' * 70)
    print(f"项目根目录: {ROOT_DIR}")
    print(f"排除目录: {', '.join(sorted(EXCLUDE_DIRS))}")
    print('=' * 70)

if __name__ == '__main__':
    stats, category_stats = scan_directory()
    print_report(stats, category_stats)
    input('\n按回车键退出...')
