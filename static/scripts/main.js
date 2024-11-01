const chat = $('#chat');
const naming = $('#name');
const selection = $('#selection');
const video_player = $('#video_player');
const examples = $('#examples');
const modal = $('#record_modal');

const video_input = $('#video_url')
const video_button = $('#send_video')

const question_input = $('#question')

/* Set an initial gender as fallback */
let gender = 'm';

let chatter;
let video_id;

$('#send_name').on('click', getGender);
$('#chatname').on('keydown', function (event) {
    if (event.key === 'Enter') {
        getGender()
    }
});

video_button.on('click', sendVideo);
video_input.on('keydown', function (event) {
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

function getGender() {
    chatter = document.getElementById('chatname').value
    fetch(`gender/${chatter}`, {
        method: 'GET'
    }).then(response => response.text()).then(data => {
        gender = data;
        naming.hide();
        selection.fadeIn();
    });
}

function sendVideo() {
    video_input.parent().hide()
    selection.find('.loader').attr('style', 'display: inline-grid');
    const video_url = video_input.val();
    const params = Object.fromEntries(new URLSearchParams(URL.parse(video_url).search));

    if (params['v']) {
        video_id = params['v']
        processVideo()
    } else {
        $('#video_error').show();
    }
}

function processVideo(id) {
    fetch(`process_video/${video_id}`, {
        method: 'POST'
    }).then(response => response.json()).then(data => {
        video_player.attr('src', `https://www.youtube.com/embed/${video_id}`);
        video_player.fadeIn();
        selection.hide();
        setupChat(data);
    });
}

function setupChat(data) {
    const raw_examples = data['examples'].replace(/'/g, '"');
    const example_questions = $.parseJSON(raw_examples);

    let content = '<ul>'
    example_questions.forEach(item => {
        content += `<li onclick="sendChat('${item}')">${item}</li>`
    })
    content += '</ul>'
    examples.append(content)
    examples.fadeIn();
    chat.fadeIn();
}

function sendRecord(formData) {
    fetch(`process_voice`, {
        method: 'POST',
        body: formData,
    }).then(response => response.text()).then(text => {
        modal.modal('hide');
        sendChat(text)
    });
}

function sendChat(voice_text = null) {
    const question = typeof (voice_text) == 'object' ? question_input.val() : voice_text
    question_input.val('')

    addChat(question)
    const answer_id = addChat('', true)
    question_input.get(0).scrollIntoView({behavior: 'smooth'});

    const payload = JSON.stringify({id: video_id, chatter: chatter, question: question});
    fetch(`question`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: payload
    }).then(response => response.json()).then(response => {
        $(`#${answer_id} .chat-content span`).html(generate_answer(response))
    });
}

function addChat(text, answer = false) {
    const id = (Math.random() + 1).toString(36).substring(2);
    const chatClass = answer ? "chat" : "chat chat-left";
    const content = answer ? '<div class="loader"></div>' : `<p>${text}</p>`

    let chatHTML = `
        <div id="${id}" class="${chatClass}">
            <div class="chat-avatar avatar avatar-online">
                <img alt="img" src="/static/images/${answer ? 'ai' : gender}.png">
                <i></i>
            </div>        
            <div class="chat-body">
                <div class="chat-content">
                    <span>${content}</span>
                    <time class="chat-time">${moment().format('h:mm:ss a')}</time>
                </div>
            </div>
        </div>
    `;

    // Append the generated HTML to the chat container
    $('.chats').append(chatHTML);
    return id;
}

function generate_answer(response) {
    content = response.answer
    if (response.timestamps) {
        content += '<ul>'
        response.timestamps.forEach((item, index) => {
            content += `<li onclick="video_position(${item})">Video Position #${index + 1}</li>`
        })
        content += '</ul>'
    }
    return content
}

function video_position(time) {
    video_player.attr('src', `https://www.youtube.com/embed/${video_id}?start=${time}&autoplay=1`);
}

document.getElementById('record').addEventListener('click', function () {
    modal.modal('show');
    $('detecting').show();

    const recordBtn = document.getElementById('record_voice');
    let mediaRecorder;
    let audioChunks = [];

    navigator.mediaDevices.getUserMedia({audio: true}).then(stream => {
        $('#detecting').hide();
        $('#instruction').show()

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = event => {
            const audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
            if (audioBlob.size > 10000) {
                const formData = new FormData();
                formData.append('file', audioBlob, 'record.wav');
                audioChunks = [];
                sendRecord(formData);
                recordBtn.removeEventListener('mousedown', startRecording);
                recordBtn.removeEventListener('mouseup', stopRecording);
            } else {
                $('#short').show();
            }
        };

        function startRecording() {
            mediaRecorder.start();
            $('#short').hide();
        }

        function stopRecording() {
            mediaRecorder.stop();
        }

        recordBtn.addEventListener('mousedown', startRecording);
        recordBtn.addEventListener('mouseup', stopRecording);
    }).catch(_err => {
        $('#detecting').hide();
        $('#mic-error').show();
        $('.recorder button').attr('disabled', true)
    });
});

