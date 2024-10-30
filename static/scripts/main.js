const chat = $('#chat');
const naming = $('#name');
const selection = $('#selection');
const video_player = $('#video_player');

/* Set an initial gender as fallback */
let gender = 'm';

document.getElementById('chatname').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        const name = document.getElementById('chatname').value
        getGender(name)
    }
});

document.getElementById('send_video').addEventListener('click', sendVideo);
document.getElementById('video_url').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        sendVideo()
    }
});

document.getElementById('ask').addEventListener('click', sendChat);
document.getElementById('question').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        sendChat()
    }
});

function getGender(name) {
    fetch(`gender/${name}`, {
        method: 'GET'
    }).then(response => response.text()).then(data => {
        gender = data;
        naming.hide();
        selection.fadeIn();
    });
}

function sendVideo() {
    const video_url = $('#video_url').val();
    const params = Object.fromEntries(new URLSearchParams(URL.parse(video_url).search));

    if (params['v']) {
        processVideo(params['v'])
    } else {
        $('#video_error').show();
    }
}

function processVideo(id) {
    fetch(`process_video/${id}`, {
        method: 'POST'
    }).then(response => response.text()).then(data => {
        video_player.attr('src', `https://www.youtube.com/embed/${id}`);
        selection.hide();
        chat.fadeIn();
    });
}

function sendChat() {
    const question = $('#question').val()
    addChat(question)
    addChat('', true)
}

function addChat(text, answer = false) {
    let chatClass = answer ? "chat" : "chat chat-left";
    let content = answer ? '<div class="loader"></div>' : `<p>${text}</p>`

    let chatHTML = `
        <div class="${chatClass}">
            <div class="chat-avatar avatar avatar-online">
                <img alt="img" src="/static/images/${answer ? 'ai' : gender}.png">
                <i></i>
            </div>        
            <div class="chat-body">
                <div class="chat-content">
                    ${content}
                    <time class="chat-time">${moment().format('h:mm:ss a')}</time>
                </div>
            </div>
        </div>
    `;

    // Append the generated HTML to the chat container
    $('.chats').append(chatHTML);
}


if (1 === 2) {
    const recordBtn = document.getElementById('recordBtn');
    let mediaRecorder;
    let audioChunks = [];

    navigator.mediaDevices.getUserMedia({audio: true}).then(stream => {
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable
            = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = event => {
            const audioBlob = new Blob(audioChunks, {
                type: 'audio/wav'
            });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioChunks = [];
        };

        recordBtn.addEventListener('mousedown', () => {
            mediaRecorder.start();
        });

        recordBtn.addEventListener('mouseup', () => {
            mediaRecorder.stop();
        });
    }).catch(err => {
        console.error('Fehler beim Zugriff auf das Mikrofon:', err);
    });
}
