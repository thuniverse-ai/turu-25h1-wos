<x-app-layout>
    @include('components.modal.confirm-modal')

    <script>
        function formatSize(bytes) {
            const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
            let size = bytes;
            let unitIndex = 0;

            while (size >= 1024 && unitIndex < units.length - 1) {
                size /= 1024;
                unitIndex++;
            }

            return size.toFixed(2) + " " + units[unitIndex];
        }

        function generatePathHtml(parent, path) {
            parent.empty();
            const parts = path.split('/').filter(Boolean);
            const Perm = {{ Auth::user()->hasPerm('tab_Manage') ? 'true' : 'false' }};
            const classes = Perm ? "text-blue-500 hover:underline cursor-pointer pr-2" : 'pr-2';
            const userId = {{ Auth::user()->id }};
            const $ul = $('<ul class="flex cloud-path"></ul>').append(
                `<li><span class="${classes}">/</span></li>`
            );

            let currentPath = '';

            parts.forEach((part, index) => {
                const adjustedPart = (parts[0] === 'homes' && index === 1 && part === String(userId)) ?
                    '{{ Auth::user()->name }}' :
                    part;

                currentPath += `/${adjustedPart}/`;
                const partPath = currentPath;
                const $partLi = $(`<li><span class="${classes}">${adjustedPart}/</span></li>`);
                if (Perm) $partLi.on('click', () => updatePath(partPath));
                $ul.append($partLi);
            });

            if (Perm) $ul.find('li:first').on('click', () => updatePath(''));
            parent.append($ul);
        }

        function updatePath(path) {
            client.listCloud(path)
                .then(response => populateFileList(response))
                .catch(console.error);
        }
        const categoryToIcon = {
            image: 'fas fa-file-image',
            audio: 'fas fa-file-audio',
            video: 'fas fa-file-video',
            html: 'fab fa-html5',
            document: 'fas fa-file-word',
            pdf: 'fas fa-file-pdf',
            text: 'fas fa-file-alt',
            archive: 'fas fa-file-archive',
            folder: 'fas fa-folder',
            file: 'fas fa-file-alt',
            code: 'fas fa-file-code',
            spreadsheet: 'fas fa-file-excel',
            presentation: 'fas fa-file-powerpoint',
            font: 'fas fa-font',
        };

        function cloud_open(obj) {
            const url = obj.data('url');
            const title = obj.prop('title');
            const isdir = obj.data('isdir');
            const publicUrl = `{{ Storage::url('root') }}${url}`;
            height = '';
            width = '';

            if (isdir) {
                client.listCloud(url)
                    .then(response => populateFileList(response))
                    .catch(error => console.error('Error:', error));
                return;
            }

            const extension = url.split('.').pop().toLowerCase();
            const $contentWrapper = $('<div>', {
                class: 'w-full h-full'
            });

            const fileTypes = {
                image: ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'tiff', 'tif', 'ico', 'heic', 'img', 'dds'],
                audio: ['mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma'],
                video: ['mp4', 'webm', 'ogv', 'mkv', 'mov', 'avi', '3gp'],
                document: ['pdf', 'html', 'htm'],
                text: ['txt', 'json', 'log', 'sql', 'csv', 'xml', 'ini', 'md', 'conf', 'config', 'yml', 'yaml', 'sh',
                    'bash', 'bat', 'c', 'cpp', 'h', 'java', 'py', 'js', 'ts', 'php', 'rb', 'go', 'cs', 'swift',
                    'rs', 'kt', 'scala', 'rst', 'adoc', 'env', 'properties', 'manifest', 'plist', 'tex'
                ]
            };

            if (fileTypes.image.includes(extension)) {
                $contentWrapper.append($('<img>', {
                    class: 'w-full h-full object-fill',
                    alt: title,
                    src: publicUrl
                }));
            } else if (fileTypes.audio.includes(extension)) {
                const $audioContainer = $('<div>', {
                        class: 'flex flex-col items-center justify-center w-full p-4 bg-gray-100 dark:bg-gray-700 rounded-lg shadow-md'
                    })
                    .append($('<audio>', {
                            controls: true,
                            autoplay: true,
                            class: 'w-full'
                        })
                        .append($('<source>', {
                            src: publicUrl,
                            type: `audio/${extension}`
                        })))
                    .append($('<span>', {
                        class: 'mt-2 text-gray-800 dark:text-gray-200',
                        text: title
                    }));
                $contentWrapper.append($audioContainer);
                height = 'auto';
            } else if (fileTypes.video.includes(extension)) {
                $contentWrapper.append($('<video>', {
                        controls: true,
                        autoplay: true,
                        class: 'w-full h-full object-fill'
                    })
                    .append($('<source>', {
                        src: publicUrl,
                        type: `video/${extension}`
                    })));
            } else if (fileTypes.document.includes(extension)) {
                const $iframe = $('<iframe>', {
                    src: publicUrl,
                    frameborder: 0
                }).addClass('w-full h-full').css({
                    width: '100%', // Ensures the iframe fills the container width
                    height: '100%', // Ensures the iframe fills the container height
                    border: 'none',
                    overflow: 'auto', // Allows scrolling if content overflows
                    "will-change": 'transform'
                });

                $contentWrapper.append($iframe);
            } else if (fileTypes.text.includes(extension)) {
                fetch(publicUrl)
                    .then(response => response.text())
                    .then(text => {
                        $contentWrapper.append($('<pre>', {
                            class: 'w-full h-full p-4 overflow-auto bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200',
                            text: text
                        }));
                        createWindow(title, $contentWrapper.html());
                    })
                    .catch(error => console.error('Error fetching text file:', error));
                return;
            } else {
                showConfirmationModal(
                    '{{ __('cloud.header.cannot_preview') }}',
                    `{{ __('cloud.label.cannot_preview') }}`,
                    () => window.location.href = publicUrl,
                    null,
                    '{{ __('cloud.button.preview') }}',
                    '{{ __('cloud.button.cancel') }}'
                );
                return;
            }

            createWindow(title, $contentWrapper.html(), width, height);
        }

        function populateFileList(data) {
            const fileList = $('#file-list');
            fileList.empty();

            data.result.explorer.forEach(item => {
                const div = $('<div></div>').addClass(
                        'hover:bg-gray-300 m-1 dark:hover:bg-gray-700 text-center overflow-hidden flex flex-col justify-center rounded-lg cursor-pointer p-2'
                    )
                    .attr({
                        title: item.name,
                        'data-isdir': item.is_directory,
                        'data-url': data.result.query_path + item.name
                    });

                const icon = $('<i></i>').addClass(`${categoryToIcon[item.icon]} text-4xl mb-1`);
                const filenameSpan = $('<span></span>').addClass(
                    'text-gray-500 dark:text-gray-300 text-xs line-clamp-3 max-w-full flex-1').css('word-wrap',
                    'break-word').text(item.name);

                const extensionSpan = item.name.startsWith('.') || !item.name.includes('.') ?
                    $('<span></span>').addClass('text-transparent').text('extension') :
                    $('<span></span>').addClass('text-black dark:text-white').text(item.icon);

                if (extensionSpan) div.append(extensionSpan);
                div.append(icon, filenameSpan);
                fileList.append(div);
            });

            const contextMenu = $('#context-menu');
            let selectedFile = null;
            $(document).off('contextmenu', '#file-list > div');
            $(document).off('click', '#file-list > div');
            $(document).off('touchstart', '#file-list > div');
            $('#open-file').off('click');
            $('#open-file-tab').off('click');
            $('#copy-file-url').off('click');
            $('#rename-file').off('click');
            $('#delete-file').off('click');
            $(document).off('touchend');
            $(document).on('contextmenu', '#file-list > div', function(event) {
                $('#open-file-tab').show();
                event.preventDefault();
                selectedFile = $(this);
                contextMenu.css({
                    display: 'block',
                    left: event.pageX + 'px',
                    top: event.pageY + 'px'
                });
                const isdir = $(this).data('isdir');
                if (isdir) {
                    $('#open-file-tab').hide();
                }
            });
            $(document).on('click', '#file-list > div', function() {
                contextMenu.hide();
                cloud_open($(this));
            });
            $('#open-file').on('click', function() {
                contextMenu.hide();
                cloud_open(selectedFile);
            });
            $('#open-file-tab').on('click', function() {
                const url = selectedFile.data('url');
                const baseUrl = window.location.origin;
                const fullUrl = baseUrl + '/storage/root' + url;
                window.open(fullUrl, '_blank');
                contextMenu.hide();
            });
            $('#copy-file-url').on('click', function() {
                const fileUrl = selectedFile.data('url');
                const baseUrl = window.location.origin;
                const fullUrl = encodeURI(baseUrl + '/storage/root' + fileUrl);

                var textArea = document.createElement("textarea");
                textArea.value = fullUrl;
                document.body.appendChild(textArea);
                textArea.select();

                try {
                    document.execCommand("copy");
                } catch (err) {
                    console.log("Copy not supported or failed: ", err);
                }

                document.body.removeChild(textArea);
                contextMenu.hide();
            });
            $('#rename-file').on('click', function() {
                const url = selectedFile.data('url');
                contextMenu.hide();
            });
            $('#delete-file').on('click', function() {
                const url = selectedFile.data('url');
                const title = selectedFile.prop('title');
                const currentPath = url.split('/').slice(0, -1).join('/');
                contextMenu.hide();

                showConfirmationModal(
                    `{{ __('cloud.header.confirm_delete') }}`,
                    `{{ __('cloud.label.about_to_delete') }}<span class="line-clamp-4" style="word-wrap:break-word">${title}</span> {{ __('cloud.label.delete_warning') }}`,
                    function() {
                        client.deleteCloud(url)
                            .then(function(response) {
                                if (response.status == 'success') {
                                    updatePath(currentPath);
                                } else {}
                            })
                            .catch(console.error);
                    },
                    null,
                    '{{ __('cloud.button.delete') }}',
                    '{{ __('cloud.button.cancel') }}',
                );
            });
            $(document).on('click', function(event) {
                if (!contextMenu.is(event.target) && contextMenu.has(event.target).length === 0 && selectedFile &&
                    !selectedFile.is(event.target) && selectedFile.has(event.target).length === 0) {
                    contextMenu.hide();
                }
            });
            $(document).on('touchstart', '#file-list > div', function(event) {
                selectedFile = $(this);
                setTimeout(() => {
                    contextMenu.css({
                        display: 'block',
                        left: event.originalEvent.touches[0].pageX + 'px',
                        top: event.originalEvent.touches[0].pageY + 'px'
                    });
                }, 500);
            });
            $(document).on('touchend', function() {
                contextMenu.hide();
            });
            generatePathHtml($('nav .cloud-path'), data.result.query_path);
        }

        function createWindow(windowName, contentTag, width, height) {
            const viewportWidth = $(window).width(),
                viewportHeight = $(window).height();
            const windowWidth = width === 'auto' ? 'auto' : width || viewportWidth * 0.75;
            const windowHeight = height === 'auto' ? 'auto' : height || viewportHeight * 0.75;

            const $window = $('<div>').addClass('window bg-white border flex flex-col border-gray-400 shadow-lg').css({
                width: windowWidth === 'auto' ? 'auto' : windowWidth + 'px',
                height: windowHeight === 'auto' ? 'auto' : windowHeight + 'px',
                position: 'absolute',
                top: windowHeight === 'auto' ? '10%' : (viewportHeight - windowHeight) / 2 +
                    'px', // Adjust top if height is auto
                left: (viewportWidth - windowWidth) / 2 + 'px'
            });

            const $titleBar = $('<div>').addClass(
                'title-bar bg-blue-600 text-white p-2 cursor-move flex justify-between items-center');
            const $title = $('<span>').addClass('text-xs line-clamp-1 max-w-full flex-1').css('word-wrap', 'break-word')
                .text(windowName);
            const $controls = $('<div>').addClass('controls space-x-2');
            const $minimizeBtn = $('<button>').addClass('minimize px-2').attr('title', 'Minimize').html(
                '<i class="fas fa-window-minimize"></i>');
            const $maximizeBtn = $('<button>').addClass('maximize px-2').attr('title', 'Maximize').html(
                '<i class="fas fa-window-maximize"></i>');
            const $closeBtn = $('<button>').addClass('close px-2').attr('title', 'Close').html(
                '<i class="fas fa-times"></i>');

            $controls.append($minimizeBtn, $maximizeBtn, $closeBtn);
            $titleBar.append($title, $controls);
            const $contentArea = $('<div>').addClass('content flex-1 p-1 overflow-hidden').attr('id', 'contentArea').html(
                contentTag);
            $window.append($titleBar, $contentArea);
            $('body').append($window);

            let originalSize = {
                    width: $window.width(),
                    height: $window.height()
                },
                originalPosition = {
                    top: $window.position().top,
                    left: $window.position().left
                };
            $window.resizable({
                handles: "n, e, s, w, ne, se, sw, nw",
                minWidth: 100,
                minHeight: 100,
                resize: function() {
                    var $iframe = $window.find('iframe');
                    if ($iframe.length > 0) {
                        $iframe.css('pointer-events', 'none');
                    }
                },
                stop: function() {
                    var $iframe = $window.find('iframe');
                    if ($iframe.length > 0) {
                        $iframe.css('pointer-events', 'auto');

                        var iframeDoc = $iframe[0].contentDocument || $iframe[0].contentWindow.document;
                        if (iframeDoc) {
                            iframeDoc.body.focus();
                        }
                    }

                    if ($iframe.length > 0) {
                        $iframe[0].style.display = 'none';
                        $iframe[0].style.display = 'block';

                        var iframeDoc = $iframe[0].contentDocument || $iframe[0].contentWindow.document;
                        if (iframeDoc) {
                            iframeDoc.body.style.overflow = 'auto';
                        }
                    }
                }
            });

            $window.draggable({
                handle: ".title-bar",
                containment: "body"
            });

            let isMinimized = false,
                isMaximized = false;

            $minimizeBtn.on("click", function() {
                if (isMinimized) {
                    $window.css({
                        height: originalSize.height + 'px',
                        overflow: 'visible'
                    });
                    isMinimized = false;
                } else {
                    originalSize.height = $window.height();
                    $window.css({
                        height: '2rem',
                        overflow: 'hidden'
                    });
                    isMinimized = true;
                }
            });

            $maximizeBtn.on("click", function() {
                if (isMaximized) {
                    $window.css({
                        width: originalSize.width + "px",
                        height: originalSize.height + "px",
                        top: originalPosition.top + "px",
                        left: originalPosition.left + "px"
                    });
                    isMaximized = false;
                } else {
                    originalSize = {
                        width: $window.width(),
                        height: $window.height()
                    };
                    originalPosition = {
                        top: $window.position().top,
                        left: $window.position().left
                    };
                    $window.css({
                        width: '100%',
                        height: '100%',
                        top: 0,
                        left: 0
                    });
                    isMaximized = true;
                }
            });

            $closeBtn.on("click", function() {
                $window.remove();
            });
        }
        updatePath('/homes/' + {{ Auth::user()->id }});
    </script>
    <div class="h-full">
        <div class="mx-auto h-full">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg h-full">
                <div class="relative p-2 text-gray-900 dark:text-gray-100 h-full flex flex-col">
                    <nav class="mb-2">
                        <ul class="flex space-x-2 cloud-path">
                        </ul>
                    </nav>

                    <!-- Error Popup -->
                    <div id="upload-error-popup"
                        class="hidden fixed inset-0 z-50 flex justify-center items-center bg-black bg-opacity-50">
                        <div class="bg-gray-500 dark:bg-gray-700 p-4 rounded-lg shadow-lg w-1/3 text-center">
                            <h3 class="text-xl text-white mb-2">Error</h3>
                            <p id="upload-error-message" class="text-white"></p>
                            <button id="close-error-popup"
                                class="mt-4 px-4 py-2 bg-gray-600 text-white rounded">Close</button>
                        </div>
                    </div>

                    <div id="file-window"
                        class="flex-grow border-2 border-gray-400 rounded-lg p-2 flex flex-col transition-colors">
                        <div class="mb-4 grid grid-cols-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 xl:grid-cols-10 2xl:grid-cols-12 mb-auto overflow-y-auto scrollbar"
                            id="file-list"></div>

                        <div id="drop-message" class="mt-2 text-center text-gray-600 dark:text-gray-400 hidden">
                            Drop to upload
                        </div>
                    </div>

                    <div id="context-menu"
                        class="hidden fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg p-2 dark:bg-gray-800 dark:border-gray-600">
                        <ul class="space-y-1">
                            <li id="open-file"
                                class="cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 px-2 py-1 rounded">
                                {{ __('cloud.button.open') }}</li>
                            <li id="open-file-tab"
                                class="cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 px-2 py-1 rounded">
                                {{ __('cloud.button.open_tab') }}</li>
                            <li id="copy-file-url"
                                class="cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 px-2 py-1 rounded">
                                {{ __('cloud.button.copy_link') }}</li>
                            <li id="rename-file"
                                class="cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 px-2 py-1 rounded">
                                {{ __('cloud.button.rename') }}</li>
                            <li id="delete-file"
                                class="cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 px-2 py-1 rounded">
                                {{ __('cloud.button.delete') }}</li>
                        </ul>
                    </div>

                    <!-- Progress Container at Bottom Right -->
                    <div id="upload-progress-container"
                        class="fixed bottom-5 right-5 w-80 max-h-[300px] overflow-y-auto overflow-x-hidden scrollbar bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg space-y-3">
                        <!-- Dynamic Progress Bars will be inserted here -->
                    </div>

                </div>
            </div>
        </div>
    </div>

    <script>
        $(document).ready(function() {
            const maxTasks = 5;
            const progressContainer = $('#upload-progress-container');

            $('#file-window').on('dragover', function(event) {
                event.preventDefault();
                $(this).removeClass('border-gray-400').addClass('border-blue-500');
                $('#drop-message').removeClass('hidden');
            });

            $('#file-window').on('drop', function(event) {
                event.preventDefault();
                $(this).removeClass('border-blue-500').addClass('border-gray-400');
                $('#drop-message').addClass('hidden');

                const files = event.originalEvent.dataTransfer.files;
                if (files.length > 0) {
                    uploadFile(files[0]);
                }
            });

            $('#file-window').on('dragleave', function() {
                $(this).removeClass('border-blue-500').addClass('border-gray-400');
                $('#drop-message').addClass('hidden');
            });

            $('#uploadButton').on('click', function() {
                $('#fileInput').click();
            });

            $('#fileInput').on('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    uploadFile(file);
                }
            });

            function showNotification(type, message, duration = 3000) {
                const id = `notification-${Date.now()}`;
                const iconClass = type === 'success' ? 'fas fa-check-circle text-green-500' :
                    type === 'error' ? 'fas fa-exclamation-circle text-red-500' :
                    'fas fa-info-circle text-blue-500';

                const notification = $('<div>')
                    .attr('id', id)
                    .addClass(
                        'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-lg rounded-lg p-4 flex items-center space-x-3 animate-slide-in-right'
                    );

                const icon = $('<i>')
                    .addClass(iconClass);

                const messageSpan = $('<span>')
                    .text(message);

                notification.append(icon, messageSpan);

                progressContainer.prepend(notification); // Append to upload-progress-container

                setTimeout(() => hideNotification(id), duration);
            }

            function hideNotification(id) {
                const notification = $(`#${id}`);
                notification.addClass('animate-slide-out-right');
                setTimeout(() => notification.remove(), 500);
            }

            function uploadFile(file) {
                const taskId = `task-${Date.now()}`;
                const taskContainer = $('<div>', {
                    id: taskId,
                    class: 'w-full bg-gray-100 dark:bg-gray-700 p-2 rounded-lg shadow-md'
                });

                const progressWrapper = $('<div>', {
                    class: 'w-full bg-gray-200 dark:bg-gray-600 rounded-full'
                });
                const progressBar = $('<div>', {
                    class: 'bg-blue-500 h-2 rounded-full',
                    style: 'width: 0%'
                });
                const progressText = $('<p>', {
                    class: 'text-sm text-gray-600 dark:text-gray-400 mt-1',
                    text: '0%'
                });

                progressWrapper.append(progressBar);
                taskContainer.append(progressWrapper, progressText);
                progressContainer.prepend(taskContainer);
                if (progressContainer.children().length > maxTasks) {
                    progressContainer.children().last().remove();
                }

                client.uploadFile(file, {
                    onProgress: function({
                        loaded,
                        total,
                        percent
                    }) {
                        if (total) {
                            progressBar.css('width', percent + '%');
                            progressText.text(Math.round(percent) + '%');
                        }
                    },
                    onSuccess: function(response) {
                        progressText.text('Upload complete!');
                        setTimeout(() => taskContainer.remove(), 2000);
                        showNotification('success', 'File uploaded successfully!');
                        updatePath(response.result.split('/storage/root')[1].replace(/\/[^/]+$/, '/'));
                    },
                    onError: function(error) {
                        progressText.text('Upload failed');
                        setTimeout(() => taskContainer.remove(), 2000);
                        showNotification('error', `Upload failed: ${error.message}`);
                    },
                });
            }

            $('#close-error-popup').on('click', function() {
                $('#upload-error-popup').addClass('hidden');
            });
        });
    </script>
</x-app-layout>
