#!/bin/sh
QS=${REQUEST_URI#${SCRIPT_NAME}?}
read -n "$CONTENT_LENGTH" QS_STRING_POST <&0
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
echo "<span class='header'><img class='logo' src='/images/merkury_rooted.png'/></span>"
}

get_post_data()
{
echo "<p>${REQUEST_METHOD}</p>"
echo "<p>$CONTENT_LENGTH</p>"
if [ "$REQUEST_METHOD" = "POST" ]; then 
    case "$CONTENT_TYPE" in
        application/multipart/form-data)
            read -n "$CONTENT_LENGTH" QUERY_STRING_POST <&0
            ;;
        text/plain)
            read -n "$CONTENT_LENGTH" QUERY_STRING_POST <&0
            ;;
     esac
fi
echo "<p>${QUERY_STRING}</p>"
}
print_data()
{





echo $1 | sed 's/\%2F/\//g' | sed 's/\%7C/\|/g' | sed 's/\%3F/?/g'

}
get_get_data()
{
form_name=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[1]}' | awk '{split($0,array,"=")} END{print array[2]}'`
qs=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[2]}' | awk '{split($0,array,"=")} END{print array[2]}'`
ppsapp=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[3]}' | awk '{split($0,array,"=")} END{print array[2]}'`
notify=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[4]}' | awk '{split($0,array,"=")} END{print array[2]}'`
motion=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[5]}' | awk '{split($0,array,"=")} END{print array[2]}'`
worker=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[6]}' | awk '{split($0,array,"=")} END{print array[2]}'`
logdir=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[7]}' | awk '{split($0,array,"=")} END{print array[2]}'`
loglvl=`echo "$QUERY_STRING" | awk '{split($0,array,"&")} END{print array[8]}' | awk '{split($0,array,"=")} END{print array[2]}'`
echo "<p>$(print_data $form_name)</p>"
echo "<p>$(print_data $qs)</p>"
echo "<p>$(print_data $ppsapp)</p>"
echo "<p>$(print_data $notify)</p>"
echo "<p>$(print_data $motion)</p>"
echo "<p>$(print_data $worker)</p>"
echo "<p>$(print_data $logdir)</p>"
echo "<p>$(print_data $loglvl)</p>"
}
header
get_get_data
