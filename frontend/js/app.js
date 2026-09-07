const API_URL = "http://127.0.0.1:5000";


// ======================================================
// COMMON HELPERS
// ======================================================

function showMessage(message, type = "info") {
    alert(message);
}

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}


// ======================================================
// PASSWORD TOGGLE
// ======================================================

document.querySelectorAll(".toggle-password").forEach(button => {

    button.addEventListener("click", function () {

        const input = this.parentElement.querySelector("input");

        if (!input) return;

        if (input.type === "password") {
            input.type = "text";
            this.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
        } else {
            input.type = "password";
            this.innerHTML = '<i class="fa-solid fa-eye"></i>';
        }
    });

});


// ======================================================
// REGISTER
// ======================================================

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const fullName =
            document.getElementById("registerName")?.value.trim();

        const email =
            document.getElementById("registerEmail")?.value.trim();

        const password =
            document.getElementById("registerPassword")?.value;

        const confirmPassword =
            document.getElementById("registerConfirmPassword")?.value;

        if (!fullName || !email || !password) {
            showMessage("Please fill all required fields.");
            return;
        }

        if (password !== confirmPassword) {
            showMessage("Passwords do not match.");
            return;
        }

        try {

            const response = await fetch(
                `${API_URL}/api/register`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        full_name: fullName,
                        email: email,
                        password: password
                    })
                }
            );

            const result = await response.json();

            if (result.success) {

                showMessage(
                    "Registration successful. Please login."
                );

                window.location.href = "login.html";

            } else {

                showMessage(result.message);
            }

        } catch (error) {

            console.error("Register error:", error);

            showMessage(
                "Unable to connect to server."
            );
        }

    });

}


// ======================================================
// LOGIN
// ======================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email =
            document.getElementById("loginEmail")?.value.trim();

        const password =
            document.getElementById("loginPassword")?.value;

        if (!email || !password) {

            showMessage(
                "Please enter email and password."
            );

            return;
        }

        try {

            const response = await fetch(
                `${API_URL}/api/login`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );

            const result = await response.json();

            if (result.success) {

                if (result.user && result.user.role === "admin") {

                    window.location.href = "admin.html";

                } else {

                    window.location.href = "dashboard.html";
                }

            } else {

                showMessage(result.message);
            }

        } catch (error) {

            console.error("Login error:", error);

            showMessage(
                "Unable to connect to server."
            );
        }

    });

}


// ======================================================
// LOGOUT
// ======================================================

async function logoutUser() {

    try {

        await fetch(
            `${API_URL}/api/logout`,
            {
                method: "POST",
                credentials: "include"
            }
        );

    } catch (error) {

        console.error("Logout error:", error);

    }

    window.location.href = "login.html";
}

window.logoutUser = logoutUser;


// ======================================================
// REPORT LOST ITEM
// ======================================================

const lostItemForm =
    document.getElementById("lostItemForm");

if (lostItemForm) {

    lostItemForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const title =
            document.getElementById("lostItemName")?.value.trim();

        const category =
            document.getElementById("lostCategory")?.value;

        const date =
            document.getElementById("lostDate")?.value;

        const description =
            document.getElementById("lostDescription")?.value.trim();

        const location =
            document.getElementById("lostLocation")?.value;

        const specificLocation =
            document.getElementById(
                "lostSpecificLocation"
            )?.value.trim();

        const locationDetails =
            document.getElementById(
                "lostLocationDetails"
            )?.value.trim();


        if (!title || !category || !date || !location) {

            showMessage(
                "Please fill all required fields."
            );

            return;
        }


        let finalLocation = location;

        if (specificLocation) {
            finalLocation += ` - ${specificLocation}`;
        }

        if (locationDetails) {
            finalLocation += ` - ${locationDetails}`;
        }


        try {

            const response = await fetch(
                `${API_URL}/api/items`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "include",
                    body: JSON.stringify({

                        title: title,

                        category: category,

                        description: description,

                        location: finalLocation,

                        item_date: date,

                        item_type: "lost"

                    })
                }
            );


            const result = await response.json();


            if (result.success) {

                showMessage(
                    "Lost item reported successfully."
                );

                window.location.href =
                    "lost-items.html";

            } else {

                showMessage(result.message);
            }


        } catch (error) {

            console.error(
                "Lost item error:",
                error
            );

            showMessage(
                "Unable to connect to server."
            );
        }

    });

}


// ======================================================
// REPORT FOUND ITEM
// ======================================================

const foundItemForm =
    document.getElementById("foundItemForm");

if (foundItemForm) {

    foundItemForm.addEventListener("submit", async function (event) {

        event.preventDefault();


        const title =
            document.getElementById(
                "foundItemName"
            )?.value.trim();


        const category =
            document.getElementById(
                "foundCategory"
            )?.value;


        const date =
            document.getElementById(
                "foundDate"
            )?.value;


        const description =
            document.getElementById(
                "foundDescription"
            )?.value.trim();


        const location =
            document.getElementById(
                "foundLocation"
            )?.value;


        const specificLocation =
            document.getElementById(
                "foundSpecificLocation"
            )?.value.trim();


        const locationDetails =
            document.getElementById(
                "foundLocationDetails"
            )?.value.trim();


        if (!title || !category || !date || !location) {

            showMessage(
                "Please fill all required fields."
            );

            return;
        }


        let finalLocation = location;


        if (specificLocation) {
            finalLocation += ` - ${specificLocation}`;
        }


        if (locationDetails) {
            finalLocation += ` - ${locationDetails}`;
        }


        try {

            const response = await fetch(
                `${API_URL}/api/items`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({

                        title: title,

                        category: category,

                        description: description,

                        location: finalLocation,

                        item_date: date,

                        item_type: "found"

                    })
                }
            );


            const result =
                await response.json();


            if (result.success) {

                showMessage(
                    "Found item reported successfully."
                );

                window.location.href =
                    "found-items.html";

            } else {

                showMessage(result.message);
            }


        } catch (error) {

            console.error(
                "Found item error:",
                error
            );

            showMessage(
                "Unable to connect to server."
            );
        }

    });

}


// ======================================================
// LOAD LOST ITEMS
// ======================================================

const lostItemsContainer =
    document.getElementById(
        "lostItemsContainer"
    );

if (lostItemsContainer) {

    async function loadLostItems() {

        try {

            const response =
                await fetch(
                    `${API_URL}/api/items`
                );

            const result =
                await response.json();


            if (!result.success) {

                lostItemsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        ${result.message}
                    </div>
                `;

                return;
            }


            const lostItems =
                result.items.filter(
                    item =>
                        item.item_type === "lost"
                );


            if (lostItems.length === 0) {

                lostItemsContainer.innerHTML = `
                    <div class="text-center py-5">

                        <i class="fa-solid fa-box-open fa-3x text-muted"></i>

                        <h4 class="mt-3">
                            No Lost Items
                        </h4>

                        <p class="text-muted">
                            No lost items have been reported yet.
                        </p>

                    </div>
                `;

                return;
            }


            function renderLostItems(items) {

                if (items.length === 0) {

                    lostItemsContainer.innerHTML = `
                        <div class="text-center py-5">
                            <h5>No matching items found.</h5>
                        </div>
                    `;

                    return;
                }


                lostItemsContainer.innerHTML =
                    items.map(item => `

                    <div class="col-md-4 mb-4">

                        <div class="card h-100 shadow-sm">

                            <div class="card-body">

                                <span class="badge bg-danger mb-2">
                                    Lost
                                </span>

                                <h5 class="fw-bold">
                                    ${item.title}
                                </h5>

                                <p class="text-muted mb-2">
                                    ${item.category}
                                </p>

                                <p>
                                    <i class="fa-solid fa-location-dot me-2"></i>
                                    ${item.location}
                                </p>

                                <p>
                                    <i class="fa-solid fa-calendar me-2"></i>
                                    ${item.item_date}
                                </p>

                                <a
                                    href="item-details.html?id=${item.id}"
                                    class="btn btn-outline-primary w-100"
                                >
                                    View Details
                                </a>

                            </div>

                        </div>

                    </div>

                `).join("");
            }


            renderLostItems(lostItems);


            const searchInput =
                document.getElementById(
                    "lostSearch"
                );

            const categorySelect =
                document.getElementById(
                    "lostCategory"
                );

            const locationSelect =
                document.getElementById(
                    "lostLocation"
                );

            const searchButton =
                document.getElementById(
                    "lostSearchButton"
                );


            function applyLostFilters() {

                let filtered =
                    [...lostItems];


                const search =
                    searchInput
                    ? searchInput.value
                        .toLowerCase()
                        .trim()
                    : "";


                const category =
                    categorySelect
                    ? categorySelect.value
                    : "";


                const location =
                    locationSelect
                    ? locationSelect.value
                    : "";


                if (search) {

                    filtered =
                        filtered.filter(item =>

                            item.title
                                .toLowerCase()
                                .includes(search)

                            ||

                            item.description
                                ?.toLowerCase()
                                .includes(search)

                        );
                }


                if (category) {

                    filtered =
                        filtered.filter(
                            item =>
                                item.category === category
                        );
                }


                if (location) {

                    filtered =
                        filtered.filter(
                            item =>
                                item.location
                                    .toLowerCase()
                                    .includes(
                                        location.toLowerCase()
                                    )
                        );
                }


                renderLostItems(filtered);
            }


            if (searchButton) {

                searchButton.addEventListener(
                    "click",
                    applyLostFilters
                );

            }


        } catch (error) {

            console.error(
                "Lost items error:",
                error
            );

            lostItemsContainer.innerHTML = `
                <div class="alert alert-danger">
                    Unable to load lost items.
                </div>
            `;
        }
    }


    loadLostItems();
}


// ======================================================
// LOAD FOUND ITEMS
// ======================================================

const foundItemsContainer =
    document.getElementById(
        "foundItemsContainer"
    );

if (foundItemsContainer) {

    async function loadFoundItems() {

        try {

            const response =
                await fetch(
                    `${API_URL}/api/items`
                );

            const result =
                await response.json();


            if (!result.success) {

                foundItemsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        ${result.message}
                    </div>
                `;

                return;
            }


            const foundItems =
                result.items.filter(
                    item =>
                        item.item_type === "found"
                );


            function renderFoundItems(items) {

                if (items.length === 0) {

                    foundItemsContainer.innerHTML = `
                        <div class="text-center py-5">

                            <i class="fa-solid fa-box-open fa-3x text-muted"></i>

                            <h5 class="mt-3">
                                No matching items found.
                            </h5>

                        </div>
                    `;

                    return;
                }


                foundItemsContainer.innerHTML =
                    items.map(item => `

                    <div class="col-md-4 mb-4">

                        <div class="card h-100 shadow-sm">

                            <div class="card-body">

                                <span class="badge bg-success mb-2">
                                    Found
                                </span>

                                <h5 class="fw-bold">
                                    ${item.title}
                                </h5>

                                <p class="text-muted">
                                    ${item.category}
                                </p>

                                <p>
                                    <i class="fa-solid fa-location-dot me-2"></i>
                                    ${item.location}
                                </p>

                                <p>
                                    <i class="fa-solid fa-calendar me-2"></i>
                                    ${item.item_date}
                                </p>

                                <a
                                    href="item-details.html?id=${item.id}"
                                    class="btn btn-outline-primary w-100"
                                >
                                    View Details
                                </a>

                            </div>

                        </div>

                    </div>

                `).join("");
            }


            renderFoundItems(foundItems);


            const searchInput =
                document.getElementById(
                    "foundSearch"
                );

            const categorySelect =
                document.getElementById(
                    "foundCategory"
                );

            const locationSelect =
                document.getElementById(
                    "foundLocation"
                );

            const searchButton =
                document.getElementById(
                    "foundSearchButton"
                );


            function applyFoundFilters() {

                let filtered =
                    [...foundItems];


                const search =
                    searchInput
                    ? searchInput.value
                        .toLowerCase()
                        .trim()
                    : "";


                const category =
                    categorySelect
                    ? categorySelect.value
                    : "";


                const location =
                    locationSelect
                    ? locationSelect.value
                    : "";


                if (search) {

                    filtered =
                        filtered.filter(item =>

                            item.title
                                .toLowerCase()
                                .includes(search)

                            ||

                            item.description
                                ?.toLowerCase()
                                .includes(search)

                        );
                }


                if (category) {

                    filtered =
                        filtered.filter(
                            item =>
                                item.category === category
                        );
                }


                if (location) {

                    filtered =
                        filtered.filter(
                            item =>
                                item.location
                                    .toLowerCase()
                                    .includes(
                                        location.toLowerCase()
                                    )
                        );
                }


                renderFoundItems(filtered);
            }


            if (searchButton) {

                searchButton.addEventListener(
                    "click",
                    applyFoundFilters
                );

            }


        } catch (error) {

            console.error(
                "Found items error:",
                error
            );

            foundItemsContainer.innerHTML = `
                <div class="alert alert-danger">
                    Unable to load found items.
                </div>
            `;
        }
    }


    loadFoundItems();
}


// ======================================================
// ITEM DETAILS
// ======================================================

const detailTitle =
    document.getElementById(
        "detailTitle"
    );

if (detailTitle) {

    async function loadItemDetails() {

        const itemId =
            getQueryParam("id");


        if (!itemId) {

            detailTitle.textContent =
                "Item not found";

            return;
        }


        try {

            const response =
                await fetch(
                    `${API_URL}/api/items/${itemId}`
                );


            const result =
                await response.json();


            if (!result.success) {

                detailTitle.textContent =
                    "Item not found";

                return;
            }


            const item =
                result.item;


            detailTitle.textContent =
                item.title || "Untitled";


            const category =
                document.getElementById(
                    "detailCategory"
                );

            if (category) {
                category.textContent =
                    item.category || "Not provided";
            }


            const description =
                document.getElementById(
                    "detailDescription"
                );

            if (description) {
                description.textContent =
                    item.description ||
                    "No description provided.";
            }


            const location =
                document.getElementById(
                    "detailLocation"
                );

            if (location) {
                location.textContent =
                    item.location || "Not provided";
            }


            const date =
                document.getElementById(
                    "detailDate"
                );

            if (date) {
                date.textContent =
                    item.item_date || "Not provided";
            }


            const reporter =
                document.getElementById(
                    "detailReporter"
                );

            if (reporter) {
                reporter.textContent =
                    item.full_name || "Unknown";
            }


            const status =
                document.getElementById(
                    "detailStatus"
                );

            if (status) {

                status.textContent =
                    item.status;

                status.className =
                    item.status === "returned"
                    ? "badge bg-success"
                    : "badge bg-primary";
            }


            const icon =
                document.getElementById(
                    "detailIcon"
                );

            if (icon) {

                icon.className =
                    item.item_type === "lost"
                    ? "fa-solid fa-circle-exclamation"
                    : "fa-solid fa-circle-check";
            }


            const mapLocation =
                document.getElementById(
                    "mapLocation"
                );

            if (mapLocation) {
                mapLocation.textContent =
                    item.location || "Location unavailable";
            }


        } catch (error) {

            console.error(
                "Item details error:",
                error
            );
        }
    }


    loadItemDetails();
}


// ======================================================
// CLAIM ITEM
// ======================================================

const claimForm =
    document.getElementById(
        "claimForm"
    );

if (claimForm) {

    claimForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const itemId =
                getQueryParam("id");


            const reason =
                document.getElementById(
                    "claimReason"
                )?.value.trim();


            const additional =
                document.getElementById(
                    "claimAdditional"
                )?.value.trim();


            if (!itemId || !reason) {

                showMessage(
                    "Please provide a claim reason."
                );

                return;
            }


            let description =
                reason;


            if (additional) {

                description +=
                    "\n\nAdditional Information:\n" +
                    additional;
            }


            try {

                const response =
                    await fetch(
                        `${API_URL}/api/claims`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            credentials: "include",

                            body: JSON.stringify({

                                item_id:
                                    Number(itemId),

                                claim_description:
                                    description
                            })
                        }
                    );


                const result =
                    await response.json();


                if (result.success) {

                    showMessage(
                        "Claim submitted successfully."
                    );


                    const modalElement =
                        document.getElementById(
                            "claimModal"
                        );


                    if (modalElement) {

                        const modal =
                            bootstrap.Modal.getInstance(
                                modalElement
                            );

                        if (modal) {
                            modal.hide();
                        }
                    }


                    claimForm.reset();

                } else {

                    showMessage(
                        result.message
                    );
                }


            } catch (error) {

                console.error(
                    "Claim error:",
                    error
                );

                showMessage(
                    "Unable to connect to server."
                );
            }

        }
    );

}


// ======================================================
// DASHBOARD
// ======================================================

const recentReports =
    document.getElementById(
        "recentReports"
    );

if (recentReports) {

    async function loadDashboard() {

        try {

            const response =
                await fetch(
                    `${API_URL}/api/dashboard`,
                    {
                        credentials: "include"
                    }
                );


            const result =
                await response.json();


            if (!result.success) {

                console.error(
                    result.message
                );

                return;
            }


            const dashboard =
                result.dashboard;


            // USER NAME

            const navUserName =
                document.getElementById(
                    "navUserName"
                );

            const dashboardUserName =
                document.getElementById(
                    "dashboardUserName"
                );


            if (navUserName) {

                navUserName.textContent =
                    dashboard.user_name ||
                    "User";
            }


            if (dashboardUserName) {

                dashboardUserName.textContent =
                    dashboard.user_name ||
                    "User";
            }


            // LOST

            const lostCount =
                document.getElementById(
                    "lostCount"
                );


            if (lostCount) {

                lostCount.textContent =
                    dashboard.lost_count || 0;
            }


            // FOUND

            const foundCount =
                document.getElementById(
                    "foundCount"
                );


            if (foundCount) {

                foundCount.textContent =
                    dashboard.found_count || 0;
            }


            // MATCH

            const matchCount =
                document.getElementById(
                    "matchCount"
                );


            if (matchCount) {

                matchCount.textContent =
                    dashboard.match_count || 0;
            }


            // CLAIM COUNT

            const claimCount =
                document.getElementById(
                    "claimCount"
                );


            if (claimCount) {

                try {

                    const claimResponse =
                        await fetch(
                            `${API_URL}/api/claims/my`,
                            {
                                credentials:
                                    "include"
                            }
                        );


                    const claimResult =
                        await claimResponse.json();


                    if (
                        claimResult.success &&
                        Array.isArray(
                            claimResult.claims
                        )
                    ) {

                        const pendingClaims =
                            claimResult.claims.filter(
                                claim =>
                                    claim.status ===
                                    "pending"
                            ).length;


                        claimCount.textContent =
                            pendingClaims;

                    } else {

                        claimCount.textContent =
                            0;
                    }


                } catch (error) {

                    console.error(
                        "Claim count error:",
                        error
                    );

                    claimCount.textContent =
                        0;
                }
            }


            // RECENT REPORTS

            const reports =
                dashboard.recent_reports || [];


            if (reports.length === 0) {

                recentReports.innerHTML = `

                    <div class="text-center py-4">

                        <i class="fa-solid fa-box-open fa-2x text-muted"></i>

                        <p class="mt-3 text-muted">
                            No reports yet.
                        </p>

                    </div>

                `;

            } else {

                recentReports.innerHTML =
                    reports.map(report => `

                    <div class="border-bottom py-3">

                        <div class="d-flex justify-content-between align-items-center">

                            <div>

                                <h6 class="mb-1 fw-bold">
                                    ${report.title}
                                </h6>

                                <small class="text-muted">
                                    ${report.category}
                                    •
                                    ${report.location}
                                </small>

                            </div>

                            <span class="badge ${
                                report.item_type === "lost"
                                ? "bg-danger"
                                : "bg-success"
                            }">
                                ${report.item_type}
                            </span>

                        </div>

                    </div>

                `).join("");
            }


        } catch (error) {

            console.error(
                "Dashboard error:",
                error
            );
        }
    }


    loadDashboard();
}


// ======================================================
// POSSIBLE MATCHES
// ======================================================

const possibleMatches =
    document.getElementById(
        "possibleMatches"
    );


if (possibleMatches) {

    async function loadPossibleMatches() {

        try {

            const response =
                await fetch(
                    `${API_URL}/api/matches`,
                    {
                        credentials: "include"
                    }
                );


            const result =
                await response.json();


            if (!result.success) {

                possibleMatches.innerHTML = `
                    <div class="alert alert-danger">
                        ${result.message}
                    </div>
                `;

                return;
            }


            const matches =
                result.matches || [];


            if (matches.length === 0) {

                possibleMatches.innerHTML = `

                    <div class="text-center py-4">

                        <i class="fa-solid fa-link-slash fa-2x text-muted"></i>

                        <p class="mt-3 text-muted">
                            No possible matches found.
                        </p>

                    </div>

                `;

                return;
            }


            possibleMatches.innerHTML =
                matches.map(match => `

                <div class="card border mb-3">

                    <div class="card-body">

                        <div class="d-flex justify-content-between">

                            <h5 class="fw-bold">
                                Possible Match
                            </h5>

                            <span class="badge bg-primary">
                                ${match.match_score}% Match
                            </span>

                        </div>

                        <hr>

                        <div class="row">

                            <div class="col-md-6">

                                <h6 class="text-danger fw-bold">
                                    Lost Item
                                </h6>

                                <p class="mb-1">
                                    ${match.lost_title}
                                </p>

                                <small class="text-muted">
                                    ${match.lost_category}
                                    •
                                    ${match.lost_location}
                                </small>

                            </div>


                            <div class="col-md-6">

                                <h6 class="text-success fw-bold">
                                    Found Item
                                </h6>

                                <p class="mb-1">
                                    ${match.found_title}
                                </p>

                                <small class="text-muted">
                                    ${match.found_category}
                                    •
                                    ${match.found_location}
                                </small>

                            </div>

                        </div>

                    </div>

                </div>

            `).join("");


        } catch (error) {

            console.error(
                "Matches error:",
                error
            );

            possibleMatches.innerHTML = `
                <div class="alert alert-danger">
                    Unable to load possible matches.
                </div>
            `;
        }
    }


    loadPossibleMatches();
}


// ======================================================
// HOME PAGE STATS
// ======================================================

const totalLost =
    document.getElementById(
        "totalLost"
    );


if (totalLost) {

    async function loadHomeStats() {

        try {

            const response =
                await fetch(
                    `${API_URL}/api/stats`
                );


            const result =
                await response.json();


            if (!result.success) {

                console.error(
                    result.message
                );

                return;
            }


            document.getElementById(
                "totalLost"
            ).textContent =
                result.stats.lost;


            document.getElementById(
                "totalFound"
            ).textContent =
                result.stats.found;


            document.getElementById(
                "totalUsers"
            ).textContent =
                result.stats.users;


            document.getElementById(
                "totalReturned"
            ).textContent =
                result.stats.returned;


        } catch (error) {

            console.error(
                "Home stats error:",
                error
            );
        }
    }


    loadHomeStats();
}


// ======================================================
// ADMIN PANEL
// ======================================================

const adminClaimsContainer =
    document.getElementById(
        "adminClaims"
    );


if (adminClaimsContainer) {


    // ==============================================
    // ADMIN STATS
    // ==============================================

    async function loadAdminStats() {

        try {

            const response =
                await fetch(
                    `${API_URL}/api/admin/stats`,
                    {
                        credentials:
                            "include"
                    }
                );


            const result =
                await response.json();


            if (!result.success) {

                console.error(
                    result.message
                );

                return;
            }


            const stats =
                result.stats;


            const adminUsers =
                document.getElementById(
                    "adminUsers"
                );

            const adminItems =
                document.getElementById(
                    "adminItems"
                );

            const adminPending =
                document.getElementById(
                    "adminPending"
                );

            const adminReturned =
                document.getElementById(
                    "adminReturned"
                );


            if (adminUsers) {
                adminUsers.textContent =
                    stats.users;
            }


            if (adminItems) {
                adminItems.textContent =
                    stats.items;
            }


            if (adminPending) {
                adminPending.textContent =
                    stats.pending_claims;
            }


            if (adminReturned) {
                adminReturned.textContent =
                    stats.returned;
            }


        } catch (error) {

            console.error(
                "Admin stats error:",
                error
            );
        }
    }


    // ==============================================
    // LOAD CLAIMS
    // ==============================================

    async function loadAdminClaims() {

        try {

            const response =
                await fetch(
                    `${API_URL}/api/admin/claims`,
                    {
                        credentials:
                            "include"
                    }
                );


            const result =
                await response.json();


            if (!result.success) {

                adminClaimsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        ${result.message}
                    </div>
                `;

                return;
            }


            const claims =
                result.claims || [];


            if (claims.length === 0) {

                adminClaimsContainer.innerHTML = `

                    <div class="text-center py-5">

                        <i class="fa-solid fa-circle-check fa-3x text-success"></i>

                        <h4 class="mt-3">
                            No Claims Found
                        </h4>

                        <p class="text-muted">
                            There are currently no claim requests.
                        </p>

                    </div>

                `;

                return;
            }


            adminClaimsContainer.innerHTML =
                claims.map(claim => {


                    let badgeClass =
                        "bg-warning text-dark";


                    if (
                        claim.claim_status ===
                        "approved"
                    ) {

                        badgeClass =
                            "bg-success";
                    }


                    if (
                        claim.claim_status ===
                        "rejected"
                    ) {

                        badgeClass =
                            "bg-danger";
                    }


                    return `

                    <div class="card border mb-4">

                        <div class="card-body">

                            <div class="d-flex justify-content-between align-items-center">

                                <h5 class="fw-bold">

                                    <i class="fa-solid fa-box me-2"></i>

                                    ${claim.item_title}

                                </h5>


                                <span class="badge ${badgeClass}">

                                    ${claim.claim_status}

                                </span>

                            </div>


                            <hr>


                            <div class="row">


                                <!-- ITEM -->

                                <div class="col-md-6">

                                    <h6 class="fw-bold">
                                        Item Information
                                    </h6>


                                    <p class="mb-1">

                                        <strong>
                                            Category:
                                        </strong>

                                        ${claim.category}

                                    </p>


                                    <p class="mb-1">

                                        <strong>
                                            Location:
                                        </strong>

                                        ${claim.location}

                                    </p>


                                    <p class="mb-1">

                                        <strong>
                                            Date:
                                        </strong>

                                        ${claim.item_date}

                                    </p>


                                    <p>

                                        <strong>
                                            Status:
                                        </strong>

                                        ${claim.item_status}

                                    </p>

                                </div>


                                <!-- USERS -->

                                <div class="col-md-6">

                                    <h6 class="fw-bold">
                                        Claimant
                                    </h6>


                                    <p class="mb-1">

                                        <strong>
                                            Name:
                                        </strong>

                                        ${claim.claimant_name}

                                    </p>


                                    <p>

                                        <strong>
                                            Email:
                                        </strong>

                                        ${claim.claimant_email}

                                    </p>


                                    <hr>


                                    <h6 class="fw-bold">
                                        Item Reporter
                                    </h6>


                                    <p class="mb-1">
                                        ${claim.reporter_name}
                                    </p>


                                    <p>
                                        ${claim.reporter_email}
                                    </p>

                                </div>

                            </div>


                            <!-- CLAIM REASON -->

                            <div class="mt-3">

                                <h6 class="fw-bold">
                                    Claim Reason
                                </h6>


                                <div class="bg-light rounded p-3">

                                    ${claim.claim_description}

                                </div>

                            </div>


                            <!-- BUTTONS -->

                            <div class="mt-4 d-flex gap-2">


                                <button
                                    class="btn btn-primary"
                                    onclick="viewAdminClaim(${claim.claim_id})"
                                >

                                    <i class="fa-solid fa-eye me-1"></i>

                                    Details

                                </button>


                                ${
                                    claim.claim_status === "pending"
                                    ? `

                                    <button
                                        class="btn btn-success"
                                        onclick="approveClaim(${claim.claim_id})"
                                    >

                                        <i class="fa-solid fa-check me-1"></i>

                                        Approve

                                    </button>


                                    <button
                                        class="btn btn-danger"
                                        onclick="rejectClaim(${claim.claim_id})"
                                    >

                                        <i class="fa-solid fa-xmark me-1"></i>

                                        Reject

                                    </button>

                                    `
                                    : ""
                                }

                            </div>


                        </div>

                    </div>

                    `;

                }).join("");


        } catch (error) {

            console.error(
                "Admin claims error:",
                error
            );


            adminClaimsContainer.innerHTML = `

                <div class="alert alert-danger">

                    Unable to connect to server.

                </div>

            `;
        }
    }


    // ==============================================
    // APPROVE CLAIM
    // ==============================================

    window.approveClaim =
        async function (claimId) {


            if (
                !confirm(
                    "Are you sure you want to approve this claim?"
                )
            ) {

                return;
            }


            try {

                const response =
                    await fetch(
                        `${API_URL}/api/admin/claims/${claimId}/approve`,
                        {
                            method: "PUT",

                            credentials:
                                "include"
                        }
                    );


                const result =
                    await response.json();


                showMessage(
                    result.message
                );


                if (result.success) {

                    await loadAdminStats();

                    await loadAdminClaims();
                }


            } catch (error) {

                console.error(
                    "Approve error:",
                    error
                );


                showMessage(
                    "Server connection failed."
                );
            }

        };


    // ==============================================
    // REJECT CLAIM
    // ==============================================

    window.rejectClaim =
        async function (claimId) {


            if (
                !confirm(
                    "Are you sure you want to reject this claim?"
                )
            ) {

                return;
            }


            try {

                const response =
                    await fetch(
                        `${API_URL}/api/admin/claims/${claimId}/reject`,
                        {
                            method: "PUT",

                            credentials:
                                "include"
                        }
                    );


                const result =
                    await response.json();


                showMessage(
                    result.message
                );


                if (result.success) {

                    await loadAdminStats();

                    await loadAdminClaims();
                }


            } catch (error) {

                console.error(
                    "Reject error:",
                    error
                );


                showMessage(
                    "Server connection failed."
                );
            }

        };


    // ==============================================
    // VIEW CLAIM DETAILS
    // ==============================================

    window.viewAdminClaim =
        async function (claimId) {

            try {

                const response =
                    await fetch(
                        `${API_URL}/api/admin/claims/${claimId}`,
                        {
                            credentials:
                                "include"
                        }
                    );


                const result =
                    await response.json();


                if (!result.success) {

                    showMessage(
                        result.message
                    );

                    return;
                }


                const claim =
                    result.claim;


                const details =
                    document.getElementById(
                        "claimDetails"
                    );


                if (!details) {
                    return;
                }


                details.innerHTML = `

                    <h4 class="fw-bold">
                        ${claim.item_title}
                    </h4>


                    <hr>


                    <h6 class="fw-bold">
                        Item Details
                    </h6>


                    <p>
                        <strong>Category:</strong>
                        ${claim.category}
                    </p>


                    <p>
                        <strong>Description:</strong>
                        ${claim.item_description ||
                        "Not provided"}
                    </p>


                    <p>
                        <strong>Location:</strong>
                        ${claim.location}
                    </p>


                    <p>
                        <strong>Date:</strong>
                        ${claim.item_date}
                    </p>


                    <p>
                        <strong>Status:</strong>
                        ${claim.item_status}
                    </p>


                    <hr>


                    <h6 class="fw-bold">
                        Claimant
                    </h6>


                    <p>
                        <strong>Name:</strong>
                        ${claim.claimant_name}
                    </p>


                    <p>
                        <strong>Email:</strong>
                        ${claim.claimant_email}
                    </p>


                    <hr>


                    <h6 class="fw-bold">
                        Item Reporter
                    </h6>


                    <p>
                        <strong>Name:</strong>
                        ${claim.reporter_name}
                    </p>


                    <p>
                        <strong>Email:</strong>
                        ${claim.reporter_email}
                    </p>


                    <hr>


                    <h6 class="fw-bold">
                        Claim Reason
                    </h6>


                    <div class="bg-light p-3 rounded">

                        ${claim.claim_description}

                    </div>

                `;


                const modalElement =
                    document.getElementById(
                        "claimDetailsModal"
                    );


                if (modalElement) {

                    const modal =
                        new bootstrap.Modal(
                            modalElement
                        );

                    modal.show();
                }


            } catch (error) {

                console.error(
                    "Claim details error:",
                    error
                );


                showMessage(
                    "Unable to load claim details."
                );
            }

        };


    // LOAD ADMIN DATA

    loadAdminStats();

    loadAdminClaims();

}


// ======================================================
// HOME SEARCH
// ======================================================

const homeSearchButton =
    document.getElementById(
        "homeSearchButton"
    );


if (homeSearchButton) {

    homeSearchButton.addEventListener(
        "click",
        function () {

            const search =
                document.getElementById(
                    "homeSearch"
                )?.value.trim();


            const category =
                document.getElementById(
                    "homeCategory"
                )?.value;


            const location =
                document.getElementById(
                    "homeLocation"
                )?.value;


            const params =
                new URLSearchParams();


            if (search) {
                params.set(
                    "search",
                    search
                );
            }


            if (category) {
                params.set(
                    "category",
                    category
                );
            }


            if (location) {
                params.set(
                    "location",
                    location
                );
            }


            window.location.href =
                `lost-items.html?${params.toString()}`;

        }
    );

}


// ======================================================
// SET LOGOUT BUTTONS
// ======================================================

document
    .querySelectorAll(
        '[data-action="logout"]'
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            logoutUser
        );

    });