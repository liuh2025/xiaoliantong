#!/bin/bash

# Skills 完整性检查脚本
# 用途：检查所有 skill 需要的文件是否齐全，以及是否有未被使用的规约文件
# 支持检查：
#   1. SKILL.md 中的 cat 命令引用
#   2. CLAUDE.md 中的 @ 引用
#   3. 子 prompt 文件中的引用

set -e

# 获取脚本所在目录的父目录（ProjectPower根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SKILLS_DIR="$PROJECT_ROOT/.claude/skills"
RULES_DIR="$PROJECT_ROOT/docs/rules"
CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"

echo "=========================================="
echo "Skills 完整性检查"
echo "=========================================="
echo ""
echo "项目根目录: $PROJECT_ROOT"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 统计变量
total_skills=0
total_files_required=0
missing_files=0
unused_files=0

# 存储所有被引用的文件
declare -A referenced_files

echo "## 第一部分：检查 SKILL.md 中的 cat 引用"
echo "=========================================="
echo ""

# 遍历所有 skill
for skill_dir in "$SKILLS_DIR"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")

        # 跳过 check 目录本身
        if [ "$skill_name" = "check" ]; then
            continue
        fi

        skill_file="$skill_dir/SKILL.md"

        if [ -f "$skill_file" ]; then
            total_skills=$((total_skills + 1))
            echo "### Skill: $skill_name"
            echo "---"

            # 提取所有 cat 命令引用的文件路径
            required_files=$(grep -oP '(?<=cat\s)docs/rules/[^\s`]+\.md' "$skill_file" 2>/dev/null || true)

            if [ -z "$required_files" ]; then
                echo "  ${YELLOW}[INFO]${NC} 此 skill 不需要加载规约文件"
                echo ""
                continue
            fi

            # 检查每个需要的文件
            while IFS= read -r file_path; do
                if [ -z "$file_path" ]; then
                    continue
                fi

                total_files_required=$((total_files_required + 1))

                # 转换为绝对路径
                abs_path="$PROJECT_ROOT/$file_path"

                # 记录被引用的文件
                referenced_files["$file_path"]=1

                # 检查文件是否存在
                if [ -f "$abs_path" ]; then
                    echo "  ${GREEN}[✓]${NC} $file_path"
                else
                    echo "  ${RED}[✗]${NC} $file_path (文件不存在)"
                    missing_files=$((missing_files + 1))
                fi
            done <<< "$required_files"

            echo ""
        fi
    fi
done

echo ""
echo "=========================================="
echo "## 第二部分：检查子 prompt 文件中的引用"
echo "=========================================="
echo ""

# 检查所有子 prompt 文件（*-prompt.md）
for prompt_file in "$SKILLS_DIR"/*/*-prompt.md; do
    if [ -f "$prompt_file" ]; then
        skill_name=$(basename "$(dirname "$prompt_file")")
        prompt_name=$(basename "$prompt_file")

        echo "### $skill_name/$prompt_name"
        echo "---"

        # 提取 @docs/rules/ 或 docs/rules/ 引用
        required_files=$(grep -oE '(docs/rules/[a-zA-Z0-9_/-]+\.md|@docs/rules/[a-zA-Z0-9_/-]+\.md)' "$prompt_file" 2>/dev/null | sed 's/^@//' || true)

        if [ -z "$required_files" ]; then
            echo "  ${YELLOW}[INFO]${NC} 无规约引用"
            echo ""
            continue
        fi

        # 检查每个需要的文件
        while IFS= read -r file_path; do
            if [ -z "$file_path" ]; then
                continue
            fi

            total_files_required=$((total_files_required + 1))
            abs_path="$PROJECT_ROOT/$file_path"
            referenced_files["$file_path"]=1

            if [ -f "$abs_path" ]; then
                echo "  ${GREEN}[✓]${NC} $file_path"
            else
                echo "  ${RED}[✗]${NC} $file_path (文件不存在)"
                missing_files=$((missing_files + 1))
            fi
        done <<< "$required_files"

        echo ""
    fi
done

echo "=========================================="
echo "## 第三部分：检查 CLAUDE.md 中的 @ 引用"
echo "=========================================="
echo ""

if [ -f "$CLAUDE_MD" ]; then
    echo "### CLAUDE.md 全局加载"
    echo "---"

    # 提取 @docs/rules/ 引用
    global_refs=$(grep -oE '@docs/rules/[a-zA-Z0-9_/-]+\.md' "$CLAUDE_MD" 2>/dev/null | sed 's/^@//' || true)

    if [ -z "$global_refs" ]; then
        echo "  ${YELLOW}[INFO]${NC} 无全局规约加载"
    else
        while IFS= read -r file_path; do
            if [ -z "$file_path" ]; then
                continue
            fi

            total_files_required=$((total_files_required + 1))
            abs_path="$PROJECT_ROOT/$file_path"
            referenced_files["$file_path"]=1

            if [ -f "$abs_path" ]; then
                echo "  ${GREEN}[✓]${NC} $file_path"
            else
                echo "  ${RED}[✗]${NC} $file_path (文件不存在)"
                missing_files=$((missing_files + 1))
            fi
        done <<< "$global_refs"
    fi

    echo ""
fi

echo ""
echo "=========================================="
echo "## 第四部分：检查未被使用的规约文件"
echo "=========================================="
echo ""

# 遍历 docs/rules 目录下的所有 .md 文件
while IFS= read -r -d '' file; do
    # 转换为相对路径
    rel_path="${file#$PROJECT_ROOT/}"

    # 检查是否被引用
    if [ -z "${referenced_files[$rel_path]}" ]; then
        echo "  ${YELLOW}[!]${NC} $rel_path (未被引用)"
        unused_files=$((unused_files + 1))
    fi
done < <(find "$RULES_DIR" -type f -name "*.md" -print0 2>/dev/null)

echo ""
echo "=========================================="
echo "## 统计摘要"
echo "=========================================="
echo ""
echo "总 Skill 数量: $total_skills"
echo "总引用文件数: $total_files_required"
echo ""

if [ $missing_files -eq 0 ]; then
    echo "${GREEN}✓ 所有需要的文件都存在${NC}"
else
    echo "${RED}✗ 缺失文件数: $missing_files${NC}"
fi

echo ""

if [ $unused_files -eq 0 ]; then
    echo "${GREEN}✓ 所有规约文件都被使用${NC}"
else
    echo "${YELLOW}! 未使用文件数: $unused_files${NC}"
fi

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="

# 返回状态码
if [ $missing_files -gt 0 ]; then
    exit 1
else
    exit 0
fi
