#!/usr/bin/env bash
set -euo pipefail

# Optional leading wrapper arguments: --distributed N [--master-port PORT].
# Everything after these arguments (or an optional --) goes unchanged to main.py.
# Relative config/data/output paths resolve from the copied project root.
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
python="${PYTHON:-python}"
processes=""
master_port=""

fail() {
  printf 'run.sh: %s\n' "$*" >&2
  exit 2
}

while (( $# )); do
  case "$1" in
    --distributed)
      (( $# >= 2 )) || fail '--distributed requires a positive process count'
      [[ -z "$processes" ]] || fail '--distributed may be specified only once'
      processes="$2"
      [[ "$processes" =~ ^[1-9][0-9]*$ ]] || fail '--distributed requires a positive process count'
      shift 2
      ;;
    --master-port)
      (( $# >= 2 )) || fail '--master-port requires a port number'
      [[ -z "$master_port" ]] || fail '--master-port may be specified only once'
      master_port="$2"
      [[ "$master_port" =~ ^[1-9][0-9]{0,4}$ ]] || fail '--master-port must be between 1 and 65535'
      (( master_port <= 65535 )) || fail '--master-port must be between 1 and 65535'
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *) break ;;
  esac
done

if [[ -z "$processes" ]]; then
  [[ -z "$master_port" ]] || fail '--master-port requires --distributed'
  cd -- "$project_root"
  exec "$python" main.py "$@"
fi

# CUDA DDP is opt-in. Use only the GPUs explicitly allocated by the caller;
# torchrun/main.py map these visible devices to local logical ranks.
visible_devices="${CUDA_VISIBLE_DEVICES:-}"
[[ "$visible_devices" =~ ^(0|[1-9][0-9]*)(,(0|[1-9][0-9]*))*$ ]] ||
  fail '--distributed requires CUDA_VISIBLE_DEVICES with explicit comma-separated GPU indices'
IFS=',' read -r -a gpu_ids <<< "$visible_devices"
[[ "${#gpu_ids[@]}" == "$processes" ]] ||
  fail '--distributed count must equal the number of CUDA_VISIBLE_DEVICES indices'
for (( i=0; i<${#gpu_ids[@]}; i++ )); do
  for (( j=0; j<i; j++ )); do
    [[ "${gpu_ids[i]}" != "${gpu_ids[j]}" ]] || fail 'CUDA_VISIBLE_DEVICES contains duplicate GPU indices'
  done
done

launch_args=(--nnodes=1 "--nproc_per_node=$processes")
if [[ -n "$master_port" ]]; then
  launch_args+=("--master_port=$master_port")
fi
cd -- "$project_root"
exec "$python" -m torch.distributed.run "${launch_args[@]}" main.py "$@"
