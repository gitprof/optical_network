
action=$1

if   [[ $action == "load" ]]; then
    cp /home/yakir/cs_web_scanner_proj/cs_web_scanner/src/main/utilities/Debug.py src/main/utilities/
    cp /home/yakir/cs_web_scanner_proj/cs_web_scanner/src/main/utilities/Misc.py src/main/utilities/
    cp /home/yakir/cs_web_scanner_proj/cs_web_scanner/src/main/Global.py src/main/Global.py
elif [[ $action == "save" ]]; then
    cp src/main/utilities/Debug.py /home/yakir/cs_web_scanner_proj/cs_web_scanner/src/main/utilities/
    cp src/main/utilities/Misc.py /home/yakir/cs_web_scanner_proj/cs_web_scanner/src/main/utilities/
    cp src/main/Global.py /home/yakir/cs_web_scanner_proj/cs_web_scanner/src/main/
else
    echo "bad action!"
fi

