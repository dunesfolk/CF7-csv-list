import pymysql, os, re, csv
from urllib.parse import unquote

# If you have MySQL connection information in .cnf file, set the file path here
cnf_path = os.path.expanduser('~/.mysql.cnf')

#SQL Queries
result = [["blog_path", "post_id", "post_title", "mail_to", "mail_bcc"]]
query = {}
query["getBlog"] = "SELECT blog_id, path FROM wp_blogs where public = 1 AND deleted = 0;"
query["getFormName"] = "SELECT id, post_content, post_name FROM wp__BLOGID__posts WHERE post_type LIKE 'page' AND post_status LIKE 'publish';"
query["getMail"] = "SELECT post_id, post_title, meta_value FROM wp__BLOGID__postmeta JOIN wp__BLOGID__posts ON wp__BLOGID__posts.ID = wp__BLOGID__postmeta.post_id WHERE meta_key LIKE '_mail';"


try:
    # Establish the connection using the .my.cnf file
    connection = pymysql.connect(
        read_default_file=cnf_path,
        db= "_DATABASENAME_"  # SET DB NAME HERE
    )


    with connection.cursor() as cursor:

        cursor.execute(query["getBlog"])
        resBlogId = cursor.fetchall()

        for wpblog in resBlogId:
            # to skip specific blog, set the blog path here
            # if wpblog[1] == "/":
            #     continue
            cursor.execute(re.sub(r'_BLOGID_', str(wpblog[0]), query["getMail"]))
            resMail = cursor.fetchall()
            for mailRow in resMail:
                meta_value = mailRow[2].split(";")
                for index, element in enumerate(meta_value):
                    # parse mail to
                    if element == 's:9:"recipient"':
                        mail_to = re.sub(r'(^s:[0-9]+: *)|(")|(^s:0:)', "", meta_value[index + 1])

                    # parse mail bcc
                    if element == 's:18:"additional_headers"':
                        mail_bcc = re.sub(r'(^s:[0-9]+:"Bcc: *)|(")|(^s:0:)', "", meta_value[index + 1])
                      
                result.append([wpblog[1], mailRow[0], mailRow[1], mail_to, mail_bcc])


except pymysql.Error as e:
    print(f"Error connecting to MySQL database: {e}")

finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("MySQL connected and closed successfully")

with open('result.csv', 'w', encoding="utf_8_sig") as f:
    write = csv.writer(f)
    write.writerows(result)

