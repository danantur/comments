fetch("api/comments",
    {
	method: "GET"})
.then( response => {
    return response.text()
})
.then(json_data => {
        let data = JSON.parse(json_data)
        for (let i in data) {
            let comment = data[i]
            console.log(comment)
            let cmd = document.createElement("div")
            let email = document.createElement("p")
            email.innerHTML = comment.email
            let text = document.createElement("p")
            text.innerHTML = comment.text
            let files = document.createElement("ul")
            files.className = "files"
            for (let i_f in comment.files) {
                let li = document.createElement("li")
                let a = document.createElement("a")
                let s = comment.files[i_f].uri.split("/")
                console.log(s)
                a.innerHTML = s[s.length - 1] + "<svg xmlns=\"http://www.w3.org/2000/svg\"  viewBox=\"0 0 100 100\" width=\"100px\" height=\"100px\"><polygon fill=\"#4b4dff\" points=\"75,82 27,82 27,20 62,20 75,33\"/><polygon fill=\"#edf7f5\" points=\"74,38 57,38 57,21 61,21 61,34 74,34\"/><path fill=\"#4343bf\" d=\"M78,85H24V13.907l37.28,1.13L78,31.758V85z M30,79h42V34.242L58.72,20.963L30,20.093V79z\"/><polygon fill=\"#3abcf8\" points=\"72,89 21,89 21,13 61,13 61,23 31,23 31,79 72,79\"/></svg>"
                a.href = comment.files[i_f].uri
                li.appendChild(a)
                files.appendChild(li)
            }
            cmd.appendChild(email)
            cmd.appendChild(text)
            cmd.appendChild(files)
            document.getElementsByTagName("body")[0].appendChild(cmd)
            document.getElementsByTagName("body")[0].appendChild(document.createElement("hr"))
        }
    }
)
.catch((smth) => console.log(smth));