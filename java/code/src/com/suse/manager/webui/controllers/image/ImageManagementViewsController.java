/*
 * Copyright (c) 2023 SUSE LLC
 *
 * This software is licensed to you under the GNU General Public License,
 * version 2 (GPLv2). There is NO WARRANTY for this software, express or
 * implied, including the implied warranties of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
 * along with this software; if not, see
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
 *
 * Red Hat trademarks are not licensed under GPLv2. No permission is
 * granted to use or replicate Red Hat trademarks that are incorporated
 * in this software or its documentation.
 */

package com.suse.manager.webui.controllers.image;

import static com.suse.manager.webui.utils.SparkApplicationHelper.withCsrfToken;
import static com.suse.manager.webui.utils.SparkApplicationHelper.withImageAdmin;
import static com.suse.manager.webui.utils.SparkApplicationHelper.withUser;
import static com.suse.manager.webui.utils.SparkApplicationHelper.withUserPreferences;
import static spark.Spark.get;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import com.google.gson.Gson;
import com.redhat.rhn.domain.image.ImageSyncProject;
import com.redhat.rhn.domain.role.Role;
import com.redhat.rhn.domain.role.RoleFactory;
import com.redhat.rhn.domain.user.User;
import com.redhat.rhn.manager.image.ImageSyncManager;
import com.suse.manager.webui.errors.NotFoundException;
import com.suse.utils.Json;

import spark.ModelAndView;
import spark.Request;
import spark.Response;
import spark.template.jade.JadeTemplateEngine;

/**
 * Spark controller class for image sync pages.
 */
public class ImageManagementViewsController {

    private static final Role ADMIN_ROLE = RoleFactory.IMAGE_ADMIN;

    private ImageManagementViewsController() { }

    /**
     * Invoked from Router. Initialize routes for image sync pages.
     *
     * @param jade the Jade engine to use to render the pages
     */
    public static void initRoutes(JadeTemplateEngine jade) {
        get("/manager/cm/imagesync",
                withUserPreferences(withCsrfToken(withUser(ImageManagementViewsController::listView))), jade);
        get("/manager/cm/imagesync/create",
                withCsrfToken(withImageAdmin(ImageManagementViewsController::createView)), jade);
        get("/manager/cm/imagesync/edit/:id",
                withCsrfToken(withImageAdmin(ImageManagementViewsController::updateView)), jade);
    }

    /**
     * Returns a view to list image sync projects
     *
     * @param req the request object
     * @param res the response object
     * @param user the authorized user
     * @return the model and view
     */
    public static ModelAndView listView(Request req, Response res, User user) {
        Map<String, Object> data = new HashMap<>();
        data.put("is_admin", user.hasRole(ADMIN_ROLE));
        return new ModelAndView(data, "controllers/image/templates/list-image-sync.jade");
    }

    /**
     * Returns a view to display create form
     *
     * @param req the request object
     * @param res the response object
     * @param user the authorized user
     * @return the model and view
     */
    public static ModelAndView createView(Request req, Response res, User user) {
        Map<String, Object> data = new HashMap<>();
        return new ModelAndView(data, "controllers/image/templates/edit-image-sync.jade");
    }

    /**
     * Returns a view to display update form
     *
     * @param req the request object
     * @param res the response object
     * @param user the authorized user
     * @return the model and view
     */
    public static ModelAndView updateView(Request req, Response res, User user) {
        Long projectId;
        try {
            projectId = Long.parseLong(req.params("id"));
        }
        catch (NumberFormatException e) {
            throw new NotFoundException();
        }

        // FIXME: Do not create an instance of ImageSyncManager each time
        Optional<ImageSyncProject> project = new ImageSyncManager().lookupProject(projectId, user);
        if (!project.isPresent()) {
            res.redirect("/rhn/manager/cm/imagesync/create");
        }

        Map<String, Object> data = new HashMap<>();
        data.put("project_id", projectId);
        return new ModelAndView(data, "controllers/image/templates/edit-image-sync.jade");
    }
}