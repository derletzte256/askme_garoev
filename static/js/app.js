const questions = document.querySelectorAll('.question')
const answers = document.querySelectorAll('.answer')

function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}

const csrftoken = getCookie('csrftoken')

function handleLikeDislike(element, endpoint, idField) {
    const likeButton = element.querySelector('.like-button')
    const dislikeButton = element.querySelector('.dislike-button')
    const id = element.dataset[idField]

    function setButtonsState(disabled) {
        if (likeButton) likeButton.disabled = disabled
        if (dislikeButton) dislikeButton.disabled = disabled
    }

    function makeRequest(actionType) {
        setButtonsState(true)
        const request = new Request(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                [idField]: id,
                'type': actionType,
            }),
        })

        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                if (data.status === 'success') {
                    element.querySelector('.rating').textContent = data.rating
                } else {
                    console.log(data)
                    setButtonsState(false)
                }
            })
            .catch((error) => {
                console.error(error)
                setButtonsState(false)
            })
    }

    if (likeButton) {
        likeButton.addEventListener('click', () => makeRequest('like'))
    }

    if (dislikeButton) {
        dislikeButton.addEventListener('click', () => makeRequest('dislike'))
    }
}

for (const question of questions) {
    handleLikeDislike(question, '/like_question/', 'questionId')
}

for (const answer of answers) {
    handleLikeDislike(answer, '/like_answer/', 'answerId')

    const correctCheckbox = answer.querySelector('.correct-checkbox')
    if (correctCheckbox) {
        correctCheckbox.addEventListener('change', () => {
            const request = new Request('/approve_answer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    'answerId': answer.dataset.answerId,
                    'questionId': answer.dataset.questionId,
                }),
            })
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === 'success') {
                        correctCheckbox.checked = data.is_correct
                    } else {
                        console.log(data)
                    }
                })
                .catch((error) => {
                    console.error(error)
                })
        })
    }
}