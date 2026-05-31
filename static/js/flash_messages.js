setTimeout(() => {

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(message => {

        message.style.opacity = "0";
        message.style.transform = "translateX(50px)";

        setTimeout(() => {
            message.remove();
        }, 500);

    });

}, 3000);