#!/bin/sh

QS=${REQUEST_URI#${SCRIPT_NAME}?}


menu()
{
  echo "<h1>Main Menu</h1>"
  echo "<p class='menu'><a href="?action=worker"> Config Motion Notifications</a><br/></p>"
  echo "<p class='menu'><a href="?action=configftp">Start FTP Server</a><br/></p>"
  echo "<p class='menu'><a href="?action=upload">Upload a File</a><br/></p>"
  echo "<p class='menu'><a href="?action=reboot">Reboot Camera</a><br/></p>"
}

upload()
{
echo "<form action=?action=upload_submit method=post enctype=multipart/form-data>"
echo "<p>File to upload: </p>"
echo "<input type=file name=file1> <input type=submit>"
echo "</form>"
}

upload_submit()
{
file=/tmp/$$-$RANDOM
CR=`printf '\r'`
printf '\r\n'
IFS="$CR"
read -r delim_line
IFS=""
while read -r line; do
    #echo "got line: $line\r\n"
    fname=$(echo $line | awk -F'filename=' '{print $2}' | awk -F'"' '{print $2}')
    if [ "$fname" != "" ]; then
     filename=$fname
     #echo "GOT FILENAME: $filename"
    fi
    test x"$line" = x"" && break
    test x"$line" = x"$CR" && break
done
cat >"$file"
tail_len=$((${#delim_line} + 6))
filesize=`stat -c"%s" "$file"`
test "$filesize" -lt "$tail_len" && exit 1
/mnt/mmc01/busybox dd if="$file" skip=$((filesize - tail_len)) bs=1 count=1000 >"$file.tail" 2>/dev/null
printf "\r\n%s--\r\n" "$delim_line" >"$file.tail.expected"
if ! /mnt/mmc01/busybox diff -q "$file.tail" "$file.tail.expected" >/dev/null; then
    printf "<html>\n<body>\nMalformed file upload"
    exit 1
fi
rm "$file.tail"
rm "$file.tail.expected"
/mnt/mmc01/busybox dd of="$file" seek=$((filesize - tail_len)) bs=1 count=0 >/dev/null 2>/dev/null
rm -f /mnt/mmc01/$filename
mv $file /mnt/mmc01/$filename
echo "<p>$filename uploaded</p>"
menu
}

worker()
{
PPSAPP_CMD=$(cat /mnt/mmc01/custom.sh | grep "/mnt/mmc01/notify")
NOTIFY_CMD=$(cat /mnt/mmc01/custom.sh | grep "/mnt/mmc01/notify" | sed 's/\/mnt\/mmc01\/ppsapp | //')
echo "<h1>Config:Notify</h1>"
NOTIFY=$(echo $NOTIFY_CMD | awk {'print $1'})
MOTION=$(echo $NOTIFY_CMD | awk {'print $2'})
WORKER=$(echo $NOTIFY_CMD | awk {'print $3'})
LOGDIR=$(echo $NOTIFY_CMD | awk {'print $4'})
LOGLVL=$(echo $NOTIFY_CMD | awk {'print $5'})
case $LOGLVL in
  "0")
    LVL="(silent)"
    ;;
  "1")
    LVL="(motion detected only)"
    ;;
  "2")
    LVL="(motion detected and worker output)"
    ;;
  "3")
    LVL="(ALL ppsapp output)"
    ;;
  *)
    LVL="(Invalid Parameter)"
    ;;
esac
echo "<form action='?' method='get'>"
echo "<input type='hidden' name='action' value='submit'/>"
echo "<input type='hidden' name='form_name' value='worker'/>"
echo "<input type='hidden' name='qs' value='${REQUEST_URI}'/>"
echo "<input type='hidden' name='ppsapp' value='${PPSAPP_CMD}'/>"
echo "<p><span class='form_label'>Notify Program: </span><input type='text' name='notify' value='${NOTIFY}'/></p>"
echo "<p><span class='form_label'>Motion phrase : </span><input type='text' name='motion' value='${MOTION}'/></p>"
echo "<p><span class='form_label'>Worker Program: </span><input type='text' name='worker' value='${WORKER}'/></p>"
echo "<p><span class='form_label'>Path to Logs  : </span><input type='text' name='logdir' value='${LOGDIR}'/></p>"
echo "<p><span class='form_label'>Logging Level : </span><input type='text' name='loglvl'value='${LOGLVL}'/><span class='form_post_label'>${LVL}</span></p>"
echo "<input class='submit' type='submit' value='Commit Changes'/>"
echo "</form>"
}
configftp()
{
echo "<h1>FTP Server Config</h1>"
echo "<p>Running FTPD Processes:</p>"
echo "<p>$(ps | grep tcpsvd | grep ftp | grep -v grep)</p>"

echo "<form action='?' method='get'>"
echo "<input type='hidden' name='action' value='startftp'/>"
echo "<p><span class='form_label'>Port Number: </span><input type='text' name='ftp_port' value='21'/></p>"
echo "<p><span class='form_label'>FTP Directory: </span><input type='text' name='ftp_directory' value='/mnt/mmc01/'/></p>"
echo "<input class='submit' type='submit' value='Start FTP Server'/>"
echo "</form>"
}

startftp()

{
ftp_port=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[2]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
ftp_directory=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[3]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
/bin/tcpsvd -vE 0.0.0.0 ${ftp_port} ftpd -w ${ftp_directory} &
echo "<p>FTP server started on port $ftp_port in $ftp_directory</p>"
menu

}

confirm_reboot()
{
echo "<h1>Confirm Reboot</h1>"
echo "<p>Are you sure you want to reboot the camera?:</p>"
echo "<p class='menu'><a href='?action=reboot_confirmed'>Reboot</a> &nbsp &nbsp <a href='?action=menu'>Cancel</a></p>"
}
reboot_confirmed()
{
echo "<h1>Reboot Confirmed</h1>"
echo "<p>Reboot confirmed.  The process should take no more than 60 seconds</p>"
echo "<p class='menu'><a href='?'>Go Home</a></p>"
reboot
}
header()
{
echo "Content-type: text/html"
echo ""
echo "<html>"
echo "<head>"
echo "<title>Merkury ROOTED</title>"
echo "<link rel='stylesheet' href='/css/config.css'/>"
echo "</head>"
echo "<body>"
echo "<span class='header'><a href='?'><img class='logo' src='/images/merkury_rooted.png'/></a></span>"
}

get_data_worker()
{
form_name=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[2]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
qs=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[3]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
ppsapp=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[4]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g' | sed 's/+/ /g' | sed 's/\%26/\&/g'`
notify=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[5]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
motion=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[6]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
worker=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[7]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
logdir=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[8]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
loglvl=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[9]}' | awk '{split($0,array,"=")} END{print array[2]}' | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'`
}
get_data_startftp()
{
ftp_port=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[2]}' | awk '{split($0,array,"=")} END{print array[2]}'`
ftp_directory=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[2]}' | awk '{split($0,array,"=")} END{print array[2]}'`
}

change_customsh()
# change_line $ppsapp $notify $motion $worker $logdir $loglvl $file
{
echo "<p>"

echo "</p>"
NEWTEXT=$(echo "/mnt/mmc01/ppsapp | $notify $motion $worker $logdir $loglvl &" | sed 's/\//\\\//g')
echo "<p><b>$ppsapp</b></p>"
echo "<p><i>$NEWTEXT</i></p>"
echo "<p>"
cat $1 | sed 's/\/mnt\/mmc01\/ppsapp/${NEWTEXT}/' > /tmp/custom.sh.new
cat /tmp/custom.sh.new
echo "</p>"
}
check_submit()
{
ACTION=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[1]}' | awk '{split($0,array,"=")} END{print array[2]}'`
case $ACTION in
  "")
    echo "menu"
    ;;
  *)
    echo $ACTION
    ;;
esac
}

error_handler()
{
echo "<p>An unhandled error has occurred. Please chose an option below to continue:</p>"
menu
}

main()
{
header
case $(check_submit) in
  "worker")
     worker                                          
    ;;                                                   
  "menu")
    menu                                                 
    ;;
  submit)
    get_data_worker
    change_customsh /tmp/custom.sh
    ;;
  startftp)
    startftp

    ;;
  configftp)
    configftp
    ;;
  startftp)
    startftp
    ;;
  reboot)
    confirm_reboot
    ;;
  reboot_confirmed)
    reboot_confirmed
    ;;
  upload)
    upload
    ;;
  upload_submit)
    upload_submit
    ;;
  *)
    error_handler
    ;;
esac
}
main
