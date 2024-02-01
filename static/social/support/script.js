var ticketAddBtn = document.querySelector('.add-ticket')
var newTicketFormContainer = document.querySelector('.ticket-form_container')
var cancelBtn = document.querySelector('.cancel-btn')

ticketAddBtn.addEventListener('click' , (e) => {
    newTicketFormContainer.style.display = 'block'
})

cancelBtn.addEventListener('click' , (e) => {
    newTicketFormContainer.style.display = 'none'
})