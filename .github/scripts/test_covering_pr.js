const Redis = require('ioredis');
const fs = require('fs').promises;

const main = async () => {
    const changedFiles = process.argv.slice(2)

    /**
     * Connects to a Redis Database
     * TODO: Move these variables to GitHub secrets of our project, only admins have rights for that.
     *       For now, it's not a big deal, as it use a read-only user.
     **/
    const redis = new Redis({
        host: 'redis-19269.c285.us-west-2-2.ec2.cloud.redislabs.com',
        port: 19269,
        username: 'read-only',
        password: 'Uyuni2023!',
        enableReadyCheck: false
    });
    let tests = new Set();

    /**
     * Loop over all the files changed in the PR and check if it's covered by a test
     **/
    for (const filepath of changedFiles) {
        var classpath = filepath.replace('java/code/src/', '');
        await redis.smembers(classpath, function(err, test_names) {
            test_names.forEach(function(test) {
                tests.add(test);
            });
        });
    }

    console.log('<html><ul><li>%s</ul></html>', Array.from(tests).join('<li>'));
    process.exit(0);
}
main();
