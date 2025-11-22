const podcastContent = document.getElementById('podcast');

// Improved intersection observer setup
const setupScrollAnimations = () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target); // Stop observing once visible
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '50px'  // Start animation slightly before element comes into view
    });

    return observer;
};

const setupBookmarkFunctionality = () => {
    const bookmarks = JSON.parse(localStorage.getItem('podcastBookmarks')) || {};

    const toggleBookmark = (sectionId) => {
        if (bookmarks[sectionId]) {
            delete bookmarks[sectionId];
        } else {
            bookmarks[sectionId] = true;
        }
        localStorage.setItem('podcastBookmarks', JSON.stringify(bookmarks));
    };

    return { bookmarks, toggleBookmark };
};

const renderContent = (data) => {
    const observer = setupScrollAnimations();
    const { bookmarks, toggleBookmark } = setupBookmarkFunctionality();

    data.forEach((content, index) => {
        const section = document.createElement('section');
        section.className = 'qa-section';
        section.id = `section-${index}`;

        const questionContainer = document.createElement('div');
        questionContainer.className = 'question-container';

        const answerContainer = document.createElement('div');
        answerContainer.className = 'answer-container';

        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'buttons-container';

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'toggle-btn';
        toggleBtn.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M6 9l6 6 6-6"/>
            </svg>`;

        const bookmarkBtn = document.createElement('button');
        bookmarkBtn.className = 'bookmark-btn';
        bookmarkBtn.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>`;

        buttonsContainer.appendChild(toggleBtn);
        buttonsContainer.appendChild(bookmarkBtn);

        if (bookmarks[`section-${index}`]) {
            bookmarkBtn.classList.add('active');
        }

        bookmarkBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleBookmark(`section-${index}`);
            bookmarkBtn.classList.toggle('active');
        });

        content.forEach((item, i) => {
            if (typeof item === 'string') {
                const questionWrapper = document.createElement('div');
                questionWrapper.className = 'question-wrapper';

                const question = document.createElement('h2');
                question.textContent = item;
                questionWrapper.appendChild(question);
                questionContainer.appendChild(questionWrapper);
                questionContainer.appendChild(buttonsContainer);
            } else {
                const answer = document.createElement('ul');
                answer.className = 'answer-list collapsed';
                answer.dataset.index = index;

                item.forEach(li => {
                    const listItem = document.createElement('li');
                    listItem.textContent = li;
                    answer.appendChild(listItem);
                });
                answerContainer.appendChild(answer);
            }
        });

        // Toggle functionality
        const toggleContent = (e) => {
            // Prevent event bubbling
            e.stopPropagation();

            // Get the current section and its components
            const currentSection = e.currentTarget.closest('.qa-section');
            const answer = currentSection.querySelector('.answer-list');
            const toggleBtn = currentSection.querySelector('.toggle-btn');
            const questionContainer = currentSection.querySelector('.question-container');

            // Early return if elements not found
            if (!answer || !toggleBtn || !questionContainer) {
                console.warn('Required elements not found');
                return;
            }

            // Close all other open sections
            const allSections = document.querySelectorAll('.qa-section');
            allSections.forEach(section => {
                if (section !== currentSection) {
                    const otherAnswer = section.querySelector('.answer-list');
                    console.log(otherAnswer);
                    const otherToggleBtn = section.querySelector('.toggle-btn');
                    const otherQuestionContainer = section.querySelector('.question-container');

                    if (otherAnswer && !otherAnswer.classList.contains('collapsed')) {
                        otherAnswer.style.maxHeight = '0';
                        otherAnswer.classList.add('collapsed');
                        otherToggleBtn?.classList.remove('rotated');
                        otherQuestionContainer?.classList.remove('active');
                    }
                }else{
                    console.log('same');
                }
            });

            // Toggle current section
            const isCollapsed = answer.classList.contains('collapsed');

            // Use requestAnimationFrame for smooth animation
            requestAnimationFrame(() => {
                answer.style.maxHeight = isCollapsed ? `${answer.scrollHeight}px` : '0';
                answer.classList.toggle('collapsed');
                toggleBtn.classList.toggle('rotated');
                questionContainer.classList.toggle('active');
            });

            // Add transition end cleanup
            answer.addEventListener('transitionend', () => {
                if (!isCollapsed) {
                    answer.style.maxHeight = '0';
                }
            }, { once: true });
        };

        questionContainer.addEventListener('click', toggleContent);

        section.appendChild(questionContainer);
        section.appendChild(answerContainer);
        podcastContent.appendChild(section);

        // Observe the section for scroll animation
        observer.observe(section);
    });
};

// Enhanced fetch with better error handling
const fetchWithRetry = async (url, retries = 3) => {
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            if (i === retries - 1) throw error;
            await sleep(1000 * Math.pow(2, i)); // Exponential backoff
        }
    }
};


// Initialize
const initApp = async () => {
    try {
        podcastContent.innerHTML = '<div class="loading-spinner"></div>';
        const data = await fetchWithRetry('/podcast');
        podcastContent.innerHTML = ''; // Clear loading spinner
        renderContent(data);
    } catch (error) {
        console.error('Failed to load podcast content:', error);
        podcastContent.innerHTML = `
            <div class="error-container">
                <div class="error-content">
                    <h2>Unable to Load Content</h2>
                    <p>${error.message}</p>
                    <button onclick="window.location.reload()">Retry</button>
                </div>
            </div>`;
    }
};

// Start the app
initApp();