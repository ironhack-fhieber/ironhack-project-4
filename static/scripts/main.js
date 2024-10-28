const chat = $('#chat');
const sidebar = $('#sidebar');
const selection = $('#selection');
const video_player = $('#video_player');

document.getElementById('send_video').addEventListener('click', (event) => {
    const video_url = $('#video_url').val();
    const params = Object.fromEntries(new URLSearchParams(URL.parse(video_url).search));

    if (params['v']) {
        video_player.attr('src', `https://www.youtube.com/embed/${params['v']}`);
        selection.hide();
        chat.fadeIn();
    } else {
        $('#video_error').show();
    }
});

document.getElementById('ask').addEventListener('click', (event) => {
    question = $('#question').val()
    addChat(question)
    addChat('', true)
});

function addChat(text, answer = false) {
    let chatClass = answer ? "chat" : "chat chat-left";
    let content = answer ? '<div class="loader"></div>' : `<p>${text}</p>`

    let chatHTML = `
        <div class="${chatClass}">
            <div class="chat-avatar avatar avatar-online">
                <img alt="img" src="/static/images/${answer ? 'ai' : 'm'}.png">
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