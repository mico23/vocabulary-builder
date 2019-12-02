// use AJAX to interact with web server and database to display the information of a word

function getWord() {
    let xhttp = new XMLHttpRequest();

    let word_caputured = "word_search=" + document.getElementById("word_search").value; //require request.form['word_search'] on the server side
    // let word_caputured = document.getElementById("word_search").value; //require request.form on the server side
    // console.log("****** DEBUG ****** " + word_caputured + " ********")
    // "word_search=" will be the key in the object sent to the server
    // if "word_search=" is not created, the document.getElementById(id).value will be the key
    // and the value of the key will be ''.

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            //console.log("*** DEBUG JS01***" + this.responseText);

            document.getElementById("show_word").innerHTML = this.responseText;
            document.getElementById("word_search").value = "";
        }
    };

    xhttp.open("POST", "result" ,true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(word_caputured);
    // console.log("*** DEBUG JS02 *** getWord() triggered.")
}

function addWord() {
    let xhttp = new XMLHttpRequest();
    let add_word = "add_word=" + document.getElementById("word").innerHTML;
    console.log(add_word);

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            // console.log(this.responseText);
            document.getElementById("word_list").innerHTML = this.responseText;
        }
    };

    xhttp.open("POST", "add_word", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(add_word);
}

function question() {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            document.getElementById("question").innerHTML = this.responseText;
        }
    };

    xhttp.open("POST", "question", true);
    xhttp.send();
}

//initialize the steps in the review
var quizStep = 0;

function check(words) {
    if (quizStep < words.length) {
        let xhttp = new XMLHttpRequest();
        let answer = "answer=" + document.getElementById("answer").value;
        answer = answer + "&wordList=" + words;
        answer = answer + "&currentStep=" + quizStep;
        console.log(answer);

        xhttp.onreadystatechange = function () {
            if (this.readyState ==4 && this.status == 200) {
                if (quizStep == words.length - 1) {
                    document.getElementById("questions").innerHTML = this.responseText;
                    quizStep = 0;
                } else {
                    document.getElementById("answer").value = "";
                    document.getElementById("word_meaning").innerHTML = this.responseText;
                    document.getElementById("quiz_progress").innerHTML = JSON.stringify(quizStep+2);
                    console.log(quizStep);
                    quizStep ++;
                    console.log(quizStep);
                }
            }
        };

        xhttp.open("POST", "check", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send(answer);
    } else {
        // to reset the list
        quizStep = 0;
    }
}

var testNum = 0;

function testDOM (words) {
    console.log(words);
    if (testNum < words.length) {
        let showWord = words[testNum]
        document.getElementById("word_meaning").innerHTML = showWord;
        testNum ++;
    } else {
        document.getElementById("word_meaning").innerHTML = 'Nothing else to show!';
    }

}
