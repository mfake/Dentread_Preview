class FileUpload {
    constructor(input) {
        this.input = input
        this.max_length = 1024 * 1024 * 10; // 10 mb
    }

    upload() {
        this.create_progress_bar();
        this.initFileUpload();
    }

initFileUpload() {
    this.file = this.input.files[0];
    this.upload_file(0, null);
}

(function ($) {
    $('#submit').on('click', (event) => {
        event.preventDefault();
        var uploader = new FileUpload(document.querySelector('#fileupload'))
        uploader.upload();
    });
})(jQuery);