function uploadChats(api_id, api_hash, session_file) {
    var input = $('input[name=chatlist' + api_id +']')
    alert('Началась массовая подписка на чаты.\nОжидайте!\nНе трогайте бота!\nКак только измениться индикация можете полноценно им пользоваться');
    
    var formData = new FormData();
    formData.append('file', input[0].files[0])
    formData.set('action','load_chats')
    formData.set('api_id',api_id)
    formData.set('api_hash', api_hash)
    formData.set('session_file', session_file)
    formData.set('start', $('input[name="in_start_' + api_id +'"]')[0].value)
    formData.set('end', $('input[name="in_end_' + api_id +'"]')[0].value)


    $.ajax({
        url: '/api',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(data) {
            if (data != 'false') {
                var link = document.createElement('a')
                link.setAttribute('href', window.location.origin + '/' + data)
                link.setAttribute('download', 'chats.txt')
                link.click()
                
            }
            window.location.reload()
            
        }
    })
}

function download_chat_list(api_id, api_hash, session_file) {
    $.ajax({
        url: '/api',
        method: 'POST',
        data: {
            'action' : 'get_list_chats',
            'api_id' : api_id,
            'api_hash' : api_hash,
            'session_file' : session_file
        },
        success: function(data) {
            if (data != 'false') {
                var link = document.createElement('a')
                link.setAttribute('href', window.location.origin + '/' + data)
                link.setAttribute('download', 'chats.txt')
                link.click()
            }
        }
    })
    
}

function bot_action(action, api_id, api_hash, session_file) {
    $.ajax({
        url: '/api',
        method: 'POST',
        data: {
            'action' : action,
            'api_id' : api_id,
            'api_hash' : api_hash,
            'session_file' : session_file
        },
        success: function(data) {
            alert(data);
            setTimeout(()=> {
                window.location.reload();
            }, 100)
        }
    })
}

function updateResponse() {
    $.ajax({
        url: '/api',
        method: 'POST',
        data: {
            'action' : 'update_response',
            'group_text' : $('textarea[name="group_responce_text"]')[0].value,
            'group_start' : $('input[name="group_responce_start"]')[0].value,
            'group_end' : $('input[name="group_responce_end"]')[0].value,
            'single_text' : $('textarea[name="single_responce_text"]')[0].value,
            'single_start' : $('input[name="single_responce_start"]')[0].value,
            'single_end' : $('input[name="single_responce_end"]')[0].value,
        },
        success: function(data) {
            alert(data)
        }
    })
}

function checkUsername(api_id, api_hash, session_file) {
    var button = $('#check'+api_id)[0]
    var usernameInput = $('#username' + api_id)[0]
    button.style="background-color:gray"
    usernameInput.style="margin-left: -15px; border-color:gray"

    $.ajax({
        url: '/api',
        method: 'POST',
        data: {
            'action' : 'check_username',
            'api_id' : api_id,
            'api_hash' : api_hash,
            'session_file' : session_file,
            'username' : usernameInput.value
        },
        success: function(data) {
            console.log(data)
            if (data == "true") {
                button.style="background-color:#03aa03bd"
                usernameInput.style="margin-left: -15px; border-color:#03aa03bd"
            } else {
                button.style="background-color:#ff0000bd"
                usernameInput.style="margin-left: -15px; border-color:#ff0000bd"
            }
        }
    })
}