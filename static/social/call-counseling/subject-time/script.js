var subjectItems = document.querySelectorAll('.subject-item')
var timeItems = document.querySelectorAll('.time-item')
var form = document.querySelector('#subjectTimeForm')
var subjectInput = document.querySelector('#subjectInput')
var timeInput = document.querySelector('#timeInput')


var activeTimeItem = document.querySelector('.time-item.active')
var time = activeTimeItem.dataset.time

var activeSubjectItem = document.querySelector('.subject-item.active')
var subjectSpan = activeSubjectItem.lastElementChild
var subject = subjectSpan.innerHTML

subjectItems.forEach(element => {
    element.addEventListener('click' , () => {
        var activeSubjectItem = document.querySelector('.subject-item.active')
        activeSubjectItem.classList.remove('active')
        
        var subjectSpan = element.lastElementChild
        subject = subjectSpan.innerHTML
        element.classList.add('active')

    })
});

timeItems.forEach(element => {
    element.addEventListener('click' , ()=> {
        var activeTimeItem = document.querySelector('.time-item.active')
        activeTimeItem.classList.remove('active')

        var timeValue = element.dataset.time
        time = timeValue
        element.classList.add('active')

    })
})


function goNext(event) {
    subjectInput.value = subject
    timeInput.value = time
    form.submit()
}