var plusBtn = document.querySelector('.plus-btn')
var fileUploadContainer = document.querySelector('.file-upload_container')
var loadingElement = document.querySelector('.loading')


function getCookie(name) {
    if (!document.cookie) {
      return null;
    }
  
    const xsrfCookies = document.cookie.split(';')
      .map(c => c.trim())
      .filter(c => c.startsWith(name + '='));
  
    if (xsrfCookies.length === 0) {
      return null;
    }
    return decodeURIComponent(xsrfCookies[0].split('=')[1]);
}


function openFileInput(event) {
    var fileInput = event.currentTarget.nextElementSibling
    fileInput.click()
}


function changeFileInput(event){
    var file = event.target.files[0]
    var thisFileName = event.target.previousElementSibling.previousElementSibling

    var thisFileChangeSpan = thisFileName.nextElementSibling.lastElementChild

    var form = event.target.parentElement
    var formData = new FormData(form);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', `/social/call-counseling/${identity}/upload-file`, true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {

            if (xhr.status === 200) {

                var response = JSON.parse(xhr.responseText);

                if (response.success) {
                    var errorList = document.querySelector('.messages')
                    var successMessage = document.createElement('li')
                    successMessage.innerHTML = "فایل با موفقیت ارسال شد."
                    successMessage.classList.add('message-item')
                    successMessage.classList.add('success')
            
                    errorList.insertAdjacentElement('afterbegin' , successMessage)
                    setTimeout(() => {
                        successMessage.remove()
                    } , 5000)

                    thisFileChangeSpan.innerHTML = 'تغییر فایل'
                    thisFileName.innerHTML = file.name.substr(0, 25)

                }
                else {
                    var errorList = document.querySelector('.messages')
                    var errorMessage = document.createElement('li')
                    errorMessage.innerHTML = "خطا در ارسال فایل ! لطفا دوباره تلاش کنید."
                    errorMessage.classList.add('message-item')
                    errorMessage.classList.add('error')
            
                    errorList.insertAdjacentElement('afterbegin' , errorMessage)
                    setTimeout(() => {
                        errorMessage.remove()
                    } , 5000)
                    console.log(response.errors)
                }

            }
            else {
                var errorList = document.querySelector('.messages')
                var errorMessage = document.createElement('li')
                errorMessage.innerHTML = "خطا در ارسال فایل ! لطفا دوباره تلاش کنید."
                errorMessage.classList.add('message-item')
                errorMessage.classList.add('error')
        
                errorList.insertAdjacentElement('afterbegin' , errorMessage)
                setTimeout(() => {
                    errorMessage.remove()
                } , 5000)
            }
        }
        loadingElement.style.display = 'none'
    };
    loadingElement.style.display = 'block'
    xhr.send(formData);

}


plusBtn.addEventListener('click' , event => {
    var ubploadedFiles = document.querySelectorAll('.file-name')
    var fileSelectedFlag = true

    ubploadedFiles.forEach(Element => {
        if (Element.innerHTML == 'فایل مورد نظر خود را انتخاب کنید') {
            fileSelectedFlag = false ;
        }
    })

    if (fileSelectedFlag) {
        var csrf_token = getCookie('csrftoken');
        var inputItemElement = `                    
        <form class="file-item" data-for="file${ubploadedFiles.length+1}">
            <span class="file-name">فایل مورد نظر خود را انتخاب کنید</span>
            <div class="input-file_btn" onclick="openFileInput(event)">
                <i class="fas fa-file-plus"></i>
                <span>انتخاب فایل</span>
            </div>
            <input type="file" name="file" style="display: none;" id="file${ubploadedFiles.length+1}" class="file-input" onchange="changeFileInput(event)">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
        </form>`
    fileUploadContainer.insertAdjacentHTML('beforeend' , inputItemElement)
    }
    else{
        var errorList = document.querySelector('.messages')
        var errorMessage = document.createElement('li')
        errorMessage.innerHTML = "لطفا ابتدا فایل قبلی را بارگزاری کنید."
        errorMessage.classList.add('message-item')
        errorMessage.classList.add('error')
  
        errorList.insertAdjacentElement('afterbegin' , errorMessage)
        setTimeout(() => {
            errorMessage.remove()
        } , 5000)
    }
})


function goNext(event) {

    var submitBtn = document.querySelector('#submitMainFormBtn')
    submitBtn.click()
}