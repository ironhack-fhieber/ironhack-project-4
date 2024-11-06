const chat = $('#chat');
const naming = $('#name');
const selection = $('#selection');
const video_player = $('#video_player');
const video_change = $('#video_change');
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

video_change.on('click', function (event) {
    $('.chats').html('')
    video_player.fadeOut();
    video_change.fadeOut();
    chat.hide();

    video_input.parent().show()
    selection.find('.loader').hide();
    selection.fadeIn();
})

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
    selection.find('.loader').attr('style', 'display: inline-grid');
    video_input.parent().hide()
    const video_url = video_input.val();
    const url = new URL(video_url);

    if (url.host === 'youtu.be') {
        video_id = url.pathname.split('/').pop();
    } else {
        const params = Object.fromEntries(new URLSearchParams(url.search));
        if (params['v']) {
            video_id = params['v'];
        }
    }

    if (video_id) {
        processVideo()
    } else {
        $('#video_error').show();
    }
}

function test(video_url) {
    const url = new URL(video_url);
    let video_id = null;

    if (url.host === 'youtu.be') {
        video_id = url.pathname.split('/').pop();
    } else {
        const params = Object.fromEntries(new URLSearchParams(url.search));
        if (params['v']) {
            video_id = params['v'];
        }
    }

    if (video_id) {
        return video_id;
    } else {
        return false
    }
}

function processVideo(id) {
    fetch(`process_video/${video_id}`, {
        method: 'POST'
    }).then(response => response.json()).then(data => {
        video_player.attr('src', `https://www.youtube.com/embed/${video_id}`);
        video_player.fadeIn();
        video_input.val('');
        video_change.fadeIn();
        selection.hide();
        setupChat(data);
    });
}

function setupChat(data) {
    const raw_examples = data['examples'].replace(/'/g, '"');
    const example_questions = $.parseJSON(raw_examples);

    const welcome = `Welcome, ${chatter}! 😊 I'm Fabi's Tube Bot, here to help you with anything related to the provided videos. 
    You can ask me questions, explore more about the content, or choose from some example questions below to get started!`

    let content = `${welcome}<ul class="examples">`
    example_questions.forEach(item => {
        content += `<li onclick="sendChat('${item}')">${item}</li>`
    })
    content += '</ul>'

    addChat(content, true)
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
    const content = answer && !text.length ? '<div class="loader"></div>' : `<p>${text}</p>`

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
        content += '<ul class="timings">'
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

