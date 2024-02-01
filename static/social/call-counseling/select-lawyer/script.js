var selectBtns = document.querySelectorAll('.select-btn')
var selectedLawyer = null
var lawyerForm = document.getElementById('lawyerForm')
var lawyerNameInput = document.getElementById('lawyerNameInput')

var activeLawyer = document.querySelector('.active')

if (activeLawyer) {
    var activeLawyerBtn = activeLawyer.firstElementChild
    activeLawyerBtn.innerHTML = 'وکیل انتخاب شده است'
    selectedLawyer = activeLawyerBtn.dataset.lawyername
}

selectBtns.forEach(selectBtn => {
    selectBtn.addEventListener('click' , setSelectedLawyer)
});

function setSelectedLawyer(event) {
    var btn = event.target
    if (selectedLawyer != null) {

        var lastActiveLawyer = document.querySelector('.active')

        lastActiveLawyer.classList.remove('active')
        lastActiveLawyer.firstElementChild.innerHTML = 'انتخاب وکیل'
    }
    
    var lawyer_box = btn.parentElement

    btn.innerHTML = 'وکیل انتخاب شده است'
    lawyer_box.classList.add('active')
    
    selectedLawyer = btn.dataset.lawyername
}

function goNext(event){
    if (selectedLawyer) {
        lawyerNameInput.value = selectedLawyer
        lawyerForm.submit()
    }
    else{
        var errorList = document.querySelector('.messages')
        var errorMessage = document.createElement('li')
        errorMessage.innerHTML = "لطفا ابتدا یک وکیل انتخاب کنید"
        errorMessage.classList.add('message-item')
        errorMessage.classList.add('error')

        errorList.insertAdjacentElement('afterbegin' , errorMessage)
        setTimeout(() => {
            errorMessage.remove()
        } , 5000)
    }
}