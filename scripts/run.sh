set -x

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_DIR}/../eval_anything" || exit 1

python __main__.py \
    --eval_info evaluate_test.yaml