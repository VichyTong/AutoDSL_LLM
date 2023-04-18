cd auto
path=../../protocols
files=$(ls $path)
for filename in $files
do
    echo $filename
    output_filename="opcode_"$filename"l"
    echo $output_filename
    if [ -f "../../output/auto/$output_filename" ];then
      continue
    fi
    python3 get_opcode.py $filename
done